#!/usr/bin/env python3

import sys
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description='Docker Security Analysis Tool')
    parser.add_argument('dockerfile', nargs='?', help='Path to the Dockerfile to analyze (optional when using --image-only)')
    parser.add_argument('-i', '--image', help='Docker image name to scan')
    parser.add_argument('-o', '--output', help='Output file for the report (default: security_report.txt)')
    parser.add_argument('--ai-only', action='store_true', help='Run only AI-based recommendations (requires Dockerfile)')
    parser.add_argument('--scan-only', action='store_true', help='Run only Dockerfile/image scanning (requires --image)')
    parser.add_argument('--image-only', action='store_true', help='Scan only the Docker image without Dockerfile analysis')
    
    args = parser.parse_args()
    
    # Validate argument combinations
    if args.image_only and args.ai_only:
        print("Error: --image-only and --ai-only cannot be used together (AI analysis requires Dockerfile)")
        sys.exit(1)
    
    if args.image_only and args.scan_only:
        print("Error: --image-only and --scan-only cannot be used together (use --image-only for image-only scanning)")
        sys.exit(1)
    
    # Validate Dockerfile requirement
    if not args.image_only and not args.dockerfile:
        print("Error: Dockerfile path is required unless using --image-only")
        print("Usage examples:")
        print("  docksec Dockerfile -i myapp:latest          # Analyze both Dockerfile and image")
        print("  docksec --image-only -i myapp:latest        # Scan only the image")
        print("  docksec --ai-only Dockerfile                # AI analysis only")
        sys.exit(1)
    
    # Validate that the Dockerfile exists (if provided)
    if args.dockerfile and not os.path.isfile(args.dockerfile):
        print(f"Error: Dockerfile not found at {args.dockerfile}")
        sys.exit(1)
    
    # Validate image requirement for image-based operations
    if (args.image_only or args.scan_only) and not args.image:
        operation = "image-only scanning" if args.image_only else "scan-only mode"
        print(f"Error: Image name is required for {operation}. Use -i/--image to specify the Docker image.")
        print("Example: docksec --image-only -i myapp:latest")
        sys.exit(1)
    
    # Determine which tools to run
    if args.image_only:
        run_ai = False
        run_scan = True
        run_dockerfile_analysis = False
    elif args.ai_only:
        run_ai = True
        run_scan = False
        run_dockerfile_analysis = True
    elif args.scan_only:
        run_ai = False
        run_scan = True
        run_dockerfile_analysis = True
    else:
        # Default: run both AI and scan if both Dockerfile and image are provided
        run_ai = bool(args.dockerfile)
        run_scan = bool(args.image)
        run_dockerfile_analysis = bool(args.dockerfile)
    
    print(f"Analysis mode: AI={'Yes' if run_ai else 'No'}, Scanner={'Yes' if run_scan else 'No'}, Image-only={'Yes' if args.image_only else 'No'}")
    
    # Run the AI-based recommendation tool
    if run_ai:
        print("\n=== Running AI-based Dockerfile analysis ===")
        try:
            # Import required modules from main.py
            from utils import (
                get_custom_logger,
                load_docker_file,
                get_llm,
                analyze_security,
                AnalsesResponse,
                ScoreResponse
            )
            from config import docker_agent_prompt, docker_score_prompt
            from pathlib import Path
            
            # Set up the same components as main.py
            logger = get_custom_logger(name='docksec_ai')
            llm = get_llm()
            Report_llm = llm.with_structured_output(AnalsesResponse, method="json_mode")
            analyser_chain = docker_agent_prompt | Report_llm
            
            # Load and analyze the Dockerfile
            filecontent = load_docker_file(docker_file_path=Path(args.dockerfile))
            
            if not filecontent:
                print("Error: No Dockerfile content found.")
                return
            
            response = analyser_chain.invoke({"filecontent": filecontent})
            analyze_security(response)
            
        except ImportError as e:
            print(f"Error: Required modules not found - {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error running AI analysis: {e}")
    
    # Run the scanner tool
    if run_scan:
        scan_type = "image-only" if args.image_only else "full"
        print(f"\n=== Running {scan_type} security scanner ===")
        try:
            from docker_scanner import DockerSecurityScanner
            
            # Initialize the scanner
            dockerfile_path = args.dockerfile if run_dockerfile_analysis else None
            scanner = DockerSecurityScanner(dockerfile_path, args.image)
            
            # Run appropriate scan based on mode
            if args.image_only:
                # Image-only scan - skip Dockerfile analysis
                print(f"Scanning Docker image: {args.image}")
                results = scanner.run_image_only_scan("CRITICAL,HIGH")
            else:
                # Full scan including Dockerfile
                results = scanner.run_full_scan("CRITICAL,HIGH")
            
            # Calculate security score
            score = scanner.get_security_score(results)
            
            # Generate all reports
            scanner.generate_all_reports(results)
            
            # Run advanced scan if available
            if hasattr(scanner, 'advanced_scan'):
                print("\n=== Running Advanced Scan ===")
                scanner.advanced_scan()
            
            print("\n=== Scanning Complete ===")
            
        except ValueError as e:
            print(f"Scanner error: {e}")
        except ImportError as e:
            print(f"Error: Scanner modules not found - {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error running scanner: {e}")
    
    if not run_ai and not run_scan:
        print("No analysis performed. Use --help for usage information.")
    else:
        print("\nAnalysis complete!")

if __name__ == "__main__":
    main()