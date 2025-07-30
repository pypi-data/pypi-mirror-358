#!/usr/bin/env python3
import argparse
import sys
import torch
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS


def setup_device():
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    map_location = torch.device(device)
    
    torch_load_original = torch.load
    def patched_torch_load(*args, **kwargs):
        if 'map_location' not in kwargs:
            kwargs['map_location'] = map_location
        return torch_load_original(*args, **kwargs)
    
    torch.load = patched_torch_load
    return device


def main():
    parser = argparse.ArgumentParser(
        description='Text-to-speech synthesis using ChatterboxTTS',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Examples:\n'
               '  gensay "Hello, world!"\n'
               '  gensay -v voice.wav "Hello, world!"\n'
               '  gensay -f input.txt -o output.wav\n'
               '  echo "Hello" | gensay -o output.wav'
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('message', nargs='?', help='Text to synthesize')
    group.add_argument('-f', '--input-file', help='Read text from file')
    
    parser.add_argument('-v', '--voice', help='Voice audio prompt file')
    parser.add_argument('-o', '--output', help='Output audio file (default: output.wav)')
    
    args = parser.parse_args()
    
    # Determine text source
    if args.message:
        text = args.message
    elif args.input_file:
        try:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                text = f.read().strip()
        except FileNotFoundError:
            print(f"Error: File '{args.input_file}' not found", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Read from stdin
        text = sys.stdin.read().strip()
    
    if not text:
        print("Error: No text to synthesize", file=sys.stderr)
        sys.exit(1)
    
    # Setup output file
    output_file = args.output or "output.wav"
    
    # Setup device and model
    device = setup_device()
    model = ChatterboxTTS.from_pretrained(device=device)
    
    # Generate audio
    try:
        wav = model.generate(
            text,
            audio_prompt_path=args.voice,
            exaggeration=2.0,
            cfg_weight=0.5
        )
        ta.save(output_file, wav, model.sr)
        print(f"Audio saved to {output_file}")
    except Exception as e:
        print(f"Error generating audio: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
