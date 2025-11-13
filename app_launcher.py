"""
app_launcher.py - Wrapper script for app.py

This launcher initializes the environment and resource management before
starting the main application. It ensures proper configuration in both
development and frozen (compiled) environments.

This file should be used as the entry point for the executable build.
"""

import sys
import os


def setup_and_launch():
    """Set up environment and launch the main application."""
    
    # Print startup banner
    print("\n" + "=" * 60)
    print("  Face Recognition Attendance System")
    print("  Version 1.0.0")
    print("=" * 60 + "\n")
    
    try:
        # Step 1: Initialize configuration
        print("Initializing application...")
        from config import initialize_application
        
        config = initialize_application()
        
        # Check if dependencies are available
        if not config['dependencies_ok']:
            # Show error dialog
            try:
                from tkinter import Tk, messagebox
                root = Tk()
                root.withdraw()
                
                missing = ', '.join(config['missing_dependencies'])
                messagebox.showerror(
                    "Missing Dependencies",
                    f"The following required libraries are missing:\n\n{missing}\n\n"
                    "The application cannot start. Please reinstall the application."
                )
                root.destroy()
            except:
                print(f"\n❌ ERROR: Missing dependencies: {config['missing_dependencies']}")
            
            return 1
        
        # Step 2: Import and run main application
        print("Starting application...\n")
        
        # Import the main app module
        import app
        
        # The app.py file has if __name__ == "__main__" block that starts the app
        # We need to trigger it manually since we're importing it
        if hasattr(app, 'main'):
            # If app.py has a main() function, call it
            app.main()
        else:
            # Otherwise, execute the main block code
            root = app.Tk()
            root.withdraw()
            app.login()
            root.mainloop()
        
        return 0
        
    except ImportError as e:
        # Handle import errors
        print(f"\n❌ ERROR: Failed to import required module: {e}")
        
        try:
            from tkinter import Tk, messagebox
            root = Tk()
            root.withdraw()
            messagebox.showerror(
                "Import Error",
                f"Failed to import required module:\n\n{e}\n\n"
                "The application cannot start. Please ensure all files are present."
            )
            root.destroy()
        except:
            pass
        
        return 1
        
    except Exception as e:
        # Handle any other errors
        print(f"\n❌ ERROR: Application failed to start: {e}")
        
        import traceback
        traceback.print_exc()
        
        try:
            from tkinter import Tk, messagebox
            root = Tk()
            root.withdraw()
            messagebox.showerror(
                "Startup Error",
                f"An error occurred during startup:\n\n{e}\n\n"
                "Please check the logs for more details."
            )
            root.destroy()
        except:
            pass
        
        return 1


def main():
    """Main entry point."""
    try:
        return setup_and_launch()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user.")
        return 130
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
