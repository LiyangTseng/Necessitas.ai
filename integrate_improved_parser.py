#!/usr/bin/env python3
"""
Integration script to replace original Lambda parser with improved version
"""

import shutil
import os
from pathlib import Path

def integrate_improved_parser():
    """Replace original Lambda parser with improved version."""
    
    print("🔧 INTEGRATING IMPROVED RESUME PARSER")
    print("=" * 50)
    
    # Define paths
    original_path = Path("infra/lambda_functions/resume_parser.py")
    improved_path = Path("infra/lambda_functions/resume_parser_improved.py")
    backup_path = Path("infra/lambda_functions/resume_parser_backup.py")
    
    # Check if files exist
    if not improved_path.exists():
        print(f"❌ Improved parser not found: {improved_path}")
        return False
    
    if not original_path.exists():
        print(f"❌ Original parser not found: {original_path}")
        return False
    
    try:
        # Create backup of original
        print("📦 Creating backup of original parser...")
        shutil.copy2(original_path, backup_path)
        print(f"✅ Backup created: {backup_path}")
        
        # Replace original with improved version
        print("🔄 Replacing original parser with improved version...")
        shutil.copy2(improved_path, original_path)
        print(f"✅ Original parser replaced: {original_path}")
        
        # Add missing import for PyPDF2 fallback
        print("🔧 Adding PyPDF2 import for fallback...")
        add_pypdf2_import(original_path)
        
        print("\n✅ INTEGRATION COMPLETE!")
        print("=" * 30)
        print("Next steps:")
        print("1. Update Terraform to include PyPDF2 dependency")
        print("2. Deploy to AWS Lambda")
        print("3. Test with sample PDFs")
        print("4. Monitor CloudWatch logs")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration failed: {str(e)}")
        return False

def add_pypdf2_import(file_path):
    """Add PyPDF2 import to the Lambda function."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Add import at the top
        if 'import io' not in content:
            content = content.replace(
                'import json\nimport boto3\nimport base64',
                'import json\nimport boto3\nimport base64\nimport io'
            )
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print("✅ PyPDF2 import added")
        
    except Exception as e:
        print(f"⚠️  Could not add PyPDF2 import: {str(e)}")

def show_terraform_update():
    """Show Terraform update needed."""
    
    print("\n📋 TERRAFORM UPDATE NEEDED:")
    print("=" * 30)
    print("Add PyPDF2 to your Lambda function dependencies:")
    print("""
# In your Terraform configuration
resource "aws_lambda_function" "resume_parser" {
  # ... existing configuration ...
  
  # Add PyPDF2 to the requirements
  environment {
    variables = {
      # ... existing variables ...
    }
  }
}

# Or in your requirements.txt for Lambda layer
# Add: PyPDF2>=3.0.0
""")

def show_testing_steps():
    """Show testing steps."""
    
    print("\n🧪 TESTING STEPS:")
    print("=" * 20)
    print("1. Deploy the updated Lambda function")
    print("2. Test with sample PDF files")
    print("3. Check CloudWatch logs for errors")
    print("4. Verify DynamoDB data storage")
    print("5. Monitor Textract usage and costs")
    print("6. Compare parsing accuracy with original")

def show_monitoring():
    """Show monitoring recommendations."""
    
    print("\n📊 MONITORING RECOMMENDATIONS:")
    print("=" * 35)
    print("1. CloudWatch Metrics:")
    print("   - Lambda execution duration")
    print("   - Lambda error rate")
    print("   - Textract API calls")
    print("   - DynamoDB write operations")
    
    print("\n2. Cost Monitoring:")
    print("   - Textract costs per document")
    print("   - Lambda execution costs")
    print("   - DynamoDB storage costs")
    
    print("\n3. Quality Metrics:")
    print("   - Parsing success rate")
    print("   - Confidence score distribution")
    print("   - Data completeness")

if __name__ == "__main__":
    success = integrate_improved_parser()
    
    if success:
        show_terraform_update()
        show_testing_steps()
        show_monitoring()
        
        print("\n🎉 READY TO DEPLOY!")
        print("Your Lambda function now uses enhanced AWS Textract integration!")
    else:
        print("\n❌ Integration failed. Please check the errors above.")
