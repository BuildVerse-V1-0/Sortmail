import os
import re

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    orig_content = content
    
    # Pydantic v2 deprecation: .dict() -> .model_dump()
    content = re.sub(r'\.dict\(', r'.model_dump(', content)
    
    if content != orig_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed Pydantic .dict() in {filepath}")

if __name__ == '__main__':
    for root, _, files in os.walk('backend'):
        for file in files:
            if file.endswith('.py'):
                fix_file(os.path.join(root, file))
