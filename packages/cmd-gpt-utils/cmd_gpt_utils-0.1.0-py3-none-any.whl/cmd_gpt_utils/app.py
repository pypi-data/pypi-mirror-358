import sys
import json
from .cli import build_parser
from .config import ConfigLoader
from .models import ModelSelector
from .api import ApiClient
from .processing import ContextManager, CotProcessor, PromptBuilder
from .exceptions import CmdGptError

class CmdGptApp:
    def run(self):
        try:
            parser = build_parser()
            args = parser.parse_args()

            # Initialize and Load configuration
            config_loader = ConfigLoader()
            config_loader.initialize_default_configs()
            config = config_loader.load(args.conf_files)

            # Select model
            model_selector = ModelSelector(config.models)
            model = model_selector.select(args.model_identifier)

            if model.openai_api_key == "sk-YOUR_API_KEY_HERE":
                raise CmdGptError(
                    f"API key for model '{model.model_name}' is a placeholder. "
                    f"Please edit your model configuration file at: {config.model_yaml_path}"
                )

            # --- Step 1 & 2: Collect and build main prompt from parts ---
            main_prompt_parts = []
            if args.prompt_file:
                with open(args.prompt_file, 'r') as f:
                    main_prompt_parts.append(f.read())
            
            if args.prompt:
                positional_separator = " " if config.prompt_concat_sp else ""
                main_prompt_parts.append(positional_separator.join(args.prompt))

            nl_separator = "\n" if config.prompt_concat_nl else ""
            main_prompt_content = nl_separator.join(main_prompt_parts)

            # --- Step 3: Handle stdin ---
            read_single_line = args.stop_at_newline or config.stop_at_newline
            history_json = ""
            if not sys.stdin.isatty():
                if args.context_mode and 'i' in args.context_mode:
                    history_json = sys.stdin.read() # History always reads the whole file
                elif not main_prompt_content:
                    if read_single_line:
                        main_prompt_content = sys.stdin.readline().strip()
                    else:
                        main_prompt_content = sys.stdin.read()
            
            if not main_prompt_content and sys.stdin.isatty():
                prompt_message = "Enter prompt (Press Enter to send):" if read_single_line else "Enter prompt (Ctrl+D to send):"
                print(prompt_message, file=sys.stderr, flush=True)
                if read_single_line:
                    main_prompt_content = sys.stdin.readline().strip()
                else:
                    main_prompt_content = sys.stdin.read()

            # --- Step 4: Validation ---
            if not main_prompt_content:
                 raise CmdGptError("Prompt cannot be empty.")

            # Build the final prompt
            prompt_builder = PromptBuilder(config, args)
            final_prompt = prompt_builder.build(main_prompt_content)

            if args.verbose >= 1:
                print("--- Final User Prompt ---", file=sys.stderr)
                print(final_prompt, file=sys.stderr)
                print("-------------------------", file=sys.stderr)

            # Build message list
            context_manager = ContextManager()
            messages = context_manager.build_message_list(
                config.system_prompt, final_prompt, history_json
            )

            if args.verbose >= 2:
                print("--- Full Messages JSON ---", file=sys.stderr)
                print(json.dumps(messages, indent=2, ensure_ascii=False), file=sys.stderr)
                print("--------------------------", file=sys.stderr)

            # Determine SSE
            use_sse = model.enable_sse
            if config.enable_sse is not None:
                use_sse = config.enable_sse
            if args.use_sse is not None:
                use_sse = args.use_sse == 'true'

            # Make API call
            api_client = ApiClient(model)
            response_iterator = api_client.call(messages, use_sse)
            
            # Process and print output
            stream_to_stdout = not (args.context_mode and 'o' in args.context_mode)
            assistant_response = ""
            cot_processor = self._setup_cot_processor(args, config, model)

            for chunk in response_iterator:
                processed_chunk = cot_processor.filter(chunk) if cot_processor else chunk
                if stream_to_stdout:
                    print(processed_chunk, end='', flush=True)
                assistant_response += chunk

            messages.append({"role": "assistant", "content": assistant_response})
            
            if not stream_to_stdout: # This means context mode with output
                final_output = context_manager.format_history_json(messages)
                print(final_output)
            else:
                # For modes that don't output history JSON, add a final newline.
                print()

        except CmdGptError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.", file=sys.stderr)
            sys.exit(1)

    def _setup_cot_processor(self, args, config, model):
        # Command line arg takes highest precedence
        if args.cot_tag is not None: # This could be True or a string
            tag = args.cot_tag if isinstance(args.cot_tag, str) else None
            return CotProcessor(tag)
        
        # Then config file setting
        if config.enable_cot is not None:
            if config.enable_cot:
                return CotProcessor(config.cot_tag)
            else:
                return None # Explicitly disabled
        
        # Finally model setting
        if model.enable_cot:
            return CotProcessor(model.cot_tag)
            
        return None


