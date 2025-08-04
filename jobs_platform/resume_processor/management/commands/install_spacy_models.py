from django.core.management.base import BaseCommand
import subprocess
import sys
import os


class Command(BaseCommand):
    help = 'Install spaCy models required for resume processing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            default='en_core_web_sm',
            help='spaCy model to install (default: en_core_web_sm)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reinstall even if model exists'
        )

    def handle(self, *args, **options):
        model_name = options['model']
        force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS(f'Installing spaCy model: {model_name}')
        )
        
        try:
            # Check if model is already installed
            if not force:
                try:
                    import spacy
                    nlp = spacy.load(model_name)
                    self.stdout.write(
                        self.style.WARNING(
                            f'Model {model_name} is already installed. '
                            'Use --force to reinstall.'
                        )
                    )
                    return
                except OSError:
                    pass  # Model not found, continue with installation
            
            # Install the model
            cmd = [sys.executable, '-m', 'spacy', 'download', model_name]
            
            self.stdout.write(f'Running command: {" ".join(cmd)}')
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            self.stdout.write(result.stdout)
            
            if result.stderr:
                self.stdout.write(
                    self.style.WARNING(f'stderr: {result.stderr}')
                )
            
            # Verify installation
            try:
                import spacy
                nlp = spacy.load(model_name)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully installed and verified model: {model_name}'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Model installation verification failed: {e}'
                    )
                )
                return
            
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Failed to install spaCy model: {e}'
                )
            )
            if e.stdout:
                self.stdout.write(f'stdout: {e.stdout}')
            if e.stderr:
                self.stdout.write(f'stderr: {e.stderr}')
            return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Unexpected error during model installation: {e}'
                )
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(
                'spaCy model installation completed successfully!'
            )
        ) 