"""
Setup script for the Rwanda Map Dashboard
Handles installation of required packages with fallback options
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and print the result"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error during {description}: {e}")
        return False

def install_packages():
    """Install required packages with fallback options"""
    
    print("🚀 Setting up Rwanda Map Dashboard")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found. Please run this script from the frontend directory.")
        return False
    
    # Method 1: Try pip install with requirements.txt
    print("\n📦 Attempting to install packages using pip...")
    if run_command("pip install -r requirements.txt", "Installing all packages from requirements.txt"):
        print("🎉 All packages installed successfully!")
        return True
    
    # Method 2: Try conda for geopandas (recommended for Windows)
    print("\n🐍 Trying conda for geopandas (recommended for Windows)...")
    conda_success = True
    
    # Install basic packages with pip
    basic_packages = ["dash==2.17.1", "plotly==5.17.0", "pandas==2.1.4"]
    for package in basic_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            conda_success = False
            break
    
    # Install geopandas with conda
    if conda_success:
        conda_success = run_command("conda install geopandas -c conda-forge -y", "Installing geopandas with conda")
    
    if conda_success:
        print("🎉 Packages installed successfully using conda!")
        return True
    
    # Method 3: Install basic packages only (fallback mode)
    print("\n⚠️ Installing basic packages only (map will use fallback visualization)...")
    basic_success = True
    
    for package in basic_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            basic_success = False
    
    if basic_success:
        print("✅ Basic packages installed. App will run with limited map functionality.")
        print("💡 To get full geographic maps, install geopandas manually:")
        print("   conda install geopandas -c conda-forge")
        print("   OR")
        print("   pip install geopandas (may require additional system dependencies)")
        return True
    
    print("❌ Failed to install required packages. Please install manually.")
    return False

def test_installation():
    """Test if the installation was successful"""
    print("\n🧪 Testing installation...")
    
    try:
        import dash
        import plotly
        import pandas
        print("✅ Core packages (dash, plotly, pandas) imported successfully")
        
        try:
            import geopandas
            print("✅ Geopandas imported successfully - full map functionality available")
        except ImportError:
            print("⚠️ Geopandas not available - will use fallback visualization")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main setup function"""
    if install_packages():
        if test_installation():
            print("\n🎉 Setup completed successfully!")
            print("\n🚀 You can now run the dashboard with:")
            print("   python app.py")
            print("\n📱 The dashboard will be available at: http://localhost:8050")
        else:
            print("\n❌ Setup completed but there are import issues.")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
