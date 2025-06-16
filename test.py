import PyPDF2
import docx2txt
import re

def parse_resume(resume_file):
    text = ""

    try:
        # Extract text from PDF or DOCX
        if resume_file.name.endswith('.pdf'):
            try:
                reader = PyPDF2.PdfReader(resume_file)
                text = " ".join(page.extract_text() or "" for page in reader.pages)
            except Exception as e:
                print("PDF parsing error:", e)
                text = ""
        elif resume_file.name.endswith('.docx'):
            try:
                text = docx2txt.process(resume_file)
            except Exception as e:
                print("DOCX parsing error:", e)
                text = ""
        else:
            try:
                text = resume_file.read().decode('utf-8', errors='ignore')
            except Exception as e:
                print("Text file parsing error:", e)
                text = ""
    except Exception as e:
        print("Unhandled resume parsing error:", e)
        text = ""

    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "skills": extract_skills(text),
        "experience": extract_experience(text),
        "education": extract_education(text),
        "projects": extract_projects(text),
    }

def extract_name(text):
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if line and line[0].isupper() and len(line.split()) <= 3:
            return line
    return "Unknown"

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else "unknown@example.com"

import re
known_skills = set([
    # Programming Languages
    'python', 'c', 'c++', 'java', 'javascript', 'typescript', 'go', 'ruby', 'php', 'html', 'css',
    'sql', 'r', 'bash', 'shell scripting', 'swift', 'kotlin', 'matlab', 'scala', 'perl', 'vhdl', 'verilog',

    # Web Development
    'react', 'angular', 'vue.js', 'svelte', 'node.js', 'express.js', 'next.js', 'nuxt.js', 'django',
    'flask', 'spring boot', 'asp.net', 'laravel', 'symfony', 'tailwind css', 'bootstrap', 'sass',
    'less', 'jquery', 'web sockets', 'web assembly', 'graphql', 'rest api', 'soap', 'json', 'xml',

    # Mobile Development
    'react native', 'flutter', 'android development', 'ios development', 'java (android)', 'swift (ios)',
    'xamarin', 'cordova', 'ionic', 'kotlin',

    # Databases
    'mysql', 'postgresql', 'sqlite', 'mongodb', 'firebase', 'oracle', 'redis', 'mariadb', 'couchdb',
    'dynamodb', 'neo4j', 'elasticsearch', 'influxdb', 'timescaledb',

    # Cloud Computing & DevOps
    'aws', 'azure', 'google cloud platform', 'digitalocean', 'linode', 'heroku', 'vercel', 'netlify',
    'docker', 'kubernetes', 'jenkins', 'ansible', 'puppet', 'chef', 'terraform', 'helm',
    'ci/cd', 'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence',

    # Operating Systems & Environments
    'linux', 'ubuntu', 'debian', 'centos', 'windows server', 'macos', 'wsl', 'virtualbox',
    'vmware', 'kvm', 'hyper-v',

    # Data Science & Analytics
    'pandas', 'numpy', 'matplotlib', 'seaborn', 'scipy', 'scikit-learn', 'statsmodels',
    'tensorflow', 'pytorch', 'keras', 'xgboost', 'lightgbm', 'catboost', 'nltk', 'spacy',
    'opencv', 'mlflow', 'dvc', 'h2o.ai', 'rapidminer', 'weka', 'knime',
    'data visualization', 'eda', 'feature engineering', 'model deployment', 'a/b testing',
    'etl', 'sql analytics', 'big data', 'hadoop', 'spark', 'hive', 'airflow',

    # Business Intelligence
    'power bi', 'tableau', 'qlikview', 'looker', 'superset', 'google data studio',
    'excel (advanced)', 'pivot tables', 'vba', 'dash (plotly)',

    # Machine Learning & AI Concepts
    'supervised learning', 'unsupervised learning', 'reinforcement learning',
    'deep learning', 'neural networks', 'convolutional neural networks',
    'recurrent neural networks', 'transformers', 'nlp', 'computer vision',
    'time series analysis', 'dimensionality reduction', 'hyperparameter tuning',
    'model interpretability', 'bias/variance tradeoff',

    # Electrical & Electronics Engineering
    'arduino', 'raspberry pi', 'esp32', 'esp8266', 'stm32', 'nrf52', 'pic microcontroller',
    'avr', 'msp430', 'ti microcontrollers', '8051', 'vlsi design', 'fpga', 'cpld',
    'verilog', 'vhdl', 'keil uvision', 'xilinx ise', 'vivado', 'altium designer',
    'proteus', 'multisim', 'ltspice', 'pspice', 'eagle', 'kicad', 'tina-ti',
    'circuit design', 'pcb layout', 'power electronics', 'signal processing',
    'analog circuits', 'digital circuits', 'power systems', 'control systems',
    'robotics', 'machine vision', 'actuators', 'sensors', 'wireless communication',
    'rf design', 'modulation techniques', 'embedded systems', 'firmware development',

    # Mechanical Engineering
    'autocad', 'solidworks', 'catia', 'creo', 'ansys', 'ansys workbench', 'fluent',
    'hypermesh', 'abaqus', 'nx', 'ptc creo', '3d modeling', '2d drafting',
    'finite element analysis', 'thermal analysis', 'mechanism design', 'machine design',
    'product design', 'hvac', 'thermodynamics', 'fluid mechanics', 'refrigeration',
    'materials science', 'gd&t', 'cnc programming', 'cam', 'mechatronics',

    # Civil Engineering
    'staad pro', 'etabs', 'sap2000', 'revit', 'autocad civil 3d', 'primavera p6',
    'ms project', 'construction management', 'building information modeling',
    'quantity surveying', 'geotechnical engineering', 'transportation engineering',
    'structural engineering', 'hydraulics', 'hydrology', 'environmental engineering',
    'soil mechanics', 'urban planning', 'surveying',

    # Robotics & Automation
    'ros', 'gazebo', 'moveit', 'opencv', 'arduino robotics', 'path planning',
    'slam', 'robot kinematics', 'robot dynamics', 'machine vision', 'urdf',
    'ros2', 'coppeliasim', 'vrep', 'robotic arms', 'automation',

    # Game Development
    'unity', 'unreal engine', 'c#', 'blueprints', 'game physics', '3d modeling',
    'blender', 'maya', 'game design', 'level design', 'shader programming',

    # Cybersecurity
    'ethical hacking', 'penetration testing', 'kali linux', 'wireshark', 'nmap',
    'burp suite', 'metasploit', 'security+ certification', 'ceh', 'firewalls',
    'siem', 'identity & access management', 'vulnerability scanning',
    'ssl/tls', 'zero trust', 'network security', 'threat modeling',

    # Soft Skills & Business
    'project management', 'agile methodologies', 'scrum', 'kanban',
    'communication skills', 'leadership', 'teamwork', 'critical thinking',
    'problem solving', 'time management', 'conflict resolution', 'creativity',
    'presentation skills', 'public speaking', 'technical writing',
    'decision making', 'adaptability', 'interpersonal skills',

    # Certifications & Methodologies
    'pmp', 'six sigma', 'iso standards', 'lean manufacturing', 'kaizen',
    'tqm', 'dfmea', 'pfmea', 'root cause analysis', '5 whys', 'fishbone diagram', 'ms office', 'google workshop',
])


def extract_skills(text):
    clean_text = text.lower()
    words = re.split(r'[\s,;•\n\-\|]+', clean_text)

    found = set()
    i = 0
    while i < len(words):
        word = words[i]
        two_word = f"{word} {words[i+1]}" if i+1 < len(words) else ''

        if word in known_skills:
            found.add(word)
        elif two_word in known_skills:
            found.add(two_word)
            i += 1
        i += 1

    return ', '.join(sorted(found)) or 'general'

def extract_experience(text):
    if "experience" in text.lower():
        return text.split("experience", 1)[-1][:1000]
    return ""

def extract_education(text):
    if "education" in text.lower():
        return text.split("education", 1)[-1][:1000]
    return ""

def extract_projects(text):
    if "projects" in text.lower():
        return text.split("projects", 1)[-1][:1000]
    return ""
