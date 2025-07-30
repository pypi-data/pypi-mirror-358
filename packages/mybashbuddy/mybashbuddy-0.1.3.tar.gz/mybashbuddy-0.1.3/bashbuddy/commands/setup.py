import os
import typer
from pathlib import Path

app = typer.Typer()

@app.command()
def setup():
    """Interactive setup for BashBuddy - configure your Gemini API key"""
    typer.echo("🚀 Welcome to BashBuddy Setup!")
    typer.echo("=" * 50)
    
    # Check if API key is already set
    current_key = os.getenv("GEMINI_API_KEY")
    if current_key:
        typer.echo(f"✅ API key is already set: {current_key[:10]}...")
        if typer.confirm("Do you want to update it?"):
            pass
        else:
            typer.echo("Setup complete! You can now use BashBuddy.")
            return
    
    typer.echo("📋 To use BashBuddy, you need a Gemini API key:")
    typer.echo("1. Go to: https://makersuite.google.com/app/apikey")
    typer.echo("2. Sign in with your Google account")
    typer.echo("3. Click 'Create API Key'")
    typer.echo("4. Copy the generated key")
    
    api_key = typer.prompt("Enter your Gemini API key", hide_input=True)
    
    if not api_key or len(api_key) < 10:
        typer.echo("❌ Invalid API key. Please try again.")
        raise typer.Exit(1)
    
    # Show setup options
    typer.echo("\n💡 Choose how to save your API key:")
    typer.echo("1. Set for current session only (temporary)")
    typer.echo("2. Add to PowerShell profile (permanent for PowerShell)")
    typer.echo("3. Add to system environment variables (permanent for all)")
    typer.echo("4. Create a .env file in current directory")
    
    choice = typer.prompt("Choose option (1-4)", type=int)
    
    if choice == 1:
        # Set for current session
        os.environ["GEMINI_API_KEY"] = api_key
        typer.echo("✅ API key set for current session!")
        typer.echo("💡 Note: This will be lost when you close the terminal.")
        
    elif choice == 2:
        # Add to PowerShell profile
        try:
            profile_path = Path.home() / "Documents" / "WindowsPowerShell" / "Microsoft.PowerShell_profile.ps1"
            profile_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(profile_path, "a") as f:
                f.write(f'\n$env:GEMINI_API_KEY = "{api_key}"\n')
            
            typer.echo(f"✅ Added to PowerShell profile: {profile_path}")
            typer.echo("💡 Restart PowerShell or run: . $PROFILE")
            
        except Exception as e:
            typer.echo(f"❌ Error: {e}")
            typer.echo("💡 You can manually add this line to your PowerShell profile:")
            typer.echo(f'$env:GEMINI_API_KEY = "{api_key}"')
    
    elif choice == 3:
        # System environment variables
        typer.echo("🔧 To add to system environment variables:")
        typer.echo("1. Press Win + R, type 'sysdm.cpl', press Enter")
        typer.echo("2. Click 'Environment Variables'")
        typer.echo("3. Under 'User variables', click 'New'")
        typer.echo("4. Variable name: GEMINI_API_KEY")
        typer.echo(f"5. Variable value: {api_key}")
        typer.echo("6. Click OK and restart your terminal")
        
    elif choice == 4:
        # Create .env file
        env_file = Path(".env")
        with open(env_file, "w") as f:
            f.write(f"GEMINI_API_KEY={api_key}\n")
        typer.echo(f"✅ Created .env file: {env_file.absolute()}")
        typer.echo("💡 Note: You'll need to load this file in your scripts")
    
    else:
        typer.echo("❌ Invalid choice. Setup cancelled.")
        raise typer.Exit(1)
    
    # Test the API key
    typer.echo("\n🧪 Testing your API key...")
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Try different models in order of preference
        models_to_try = [
            "gemini-2.0-flash-exp",  # Latest experimental
            "gemini-2.0-flash",      # Stable flash model
            "gemini-1.5-flash",      # Previous flash model
            "gemini-1.5-pro",        # Pro model
            "gemini-pro",            # Original pro model
        ]
        
        working_model = None
        for model_name in models_to_try:
            try:
                typer.echo(f"🔄 Testing model: {model_name}")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Hello")
                working_model = model_name
                typer.echo(f"✅ API key works with model: {model_name}")
                break
            except Exception as e:
                typer.echo(f"❌ Model {model_name} not available: {str(e)[:50]}...")
                continue
        
        if not working_model:
            typer.echo("❌ No compatible Gemini models found!")
            typer.echo("💡 This could be due to:")
            typer.echo("   • API key doesn't have access to any Gemini models")
            typer.echo("   • API key is invalid or expired")
            typer.echo("   • Network connectivity issues")
            typer.echo("🔧 Please check your API key and try again.")
            raise typer.Exit(1)
            
    except Exception as e:
        typer.echo(f"❌ API key test failed: {e}")
        typer.echo("💡 Please check your key and try again.")
        raise typer.Exit(1)
    
    typer.echo("\n🎉 Setup complete! You can now use BashBuddy commands:")
    typer.echo("• mybashbuddy generate 'your command'")
    typer.echo("• mybashbuddy explain 'your command'")
    typer.echo("• mybashbuddy fix 'your command'")
    typer.echo("• mybashbuddy ask 'your question'")

if __name__ == "__main__":
    app() 