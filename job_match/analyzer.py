import re
from difflib import SequenceMatcher

SKILL_TAXONOMY = {
    'Programming Languages': [
        'Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'C#', 'Ruby', 'Go', 'Rust',
        'PHP', 'Swift', 'Kotlin', 'Scala', 'Perl', 'R', 'MATLAB', 'Dart', 'Lua', 'Haskell',
        'Elixir', 'Clojure', 'Groovy', 'Shell', 'Bash', 'SQL', 'HTML', 'CSS', 'Sass', 'LESS',
        'GraphQL', 'Assembly', 'Objective-C', 'Fortran', 'COBOL', 'Delphi', 'Visual Basic',
        'PL/SQL', 'T-SQL', 'Solidity', 'WebAssembly',
    ],
    'Frameworks & Libraries': [
        'Django', 'Flask', 'FastAPI', 'React', 'Angular', 'Vue.js', 'Svelte', 'Next.js',
        'Nuxt.js', 'Express.js', 'Node.js', 'Spring', 'Spring Boot', 'Laravel', 'Symfony',
        'Ruby on Rails', 'ASP.NET', '.NET Core', 'ASP.NET Core', 'Blazor', 'jQuery',
        'Bootstrap', 'Tailwind CSS', 'Material UI', 'Chakra UI', 'Shadcn UI',
        'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn', 'Pandas', 'NumPy', 'OpenCV',
        'Hugging Face', 'LangChain', 'LangGraph', 'LlamaIndex', 'Celery', 'RabbitMQ',
        'Kafka', 'gRPC', 'REST', 'GraphQL', 'Apollo', 'Redux', 'Zustand', 'Jest',
        'PyTest', 'Selenium', 'Cypress', 'Playwright', 'Mocha', 'Chai',
    ],
    'Databases & Storage': [
        'PostgreSQL', 'MySQL', 'SQLite', 'MongoDB', 'Redis', 'Elasticsearch', 'Cassandra',
        'MariaDB', 'Oracle', 'SQL Server', 'DynamoDB', 'Firebase', 'Supabase', 'Neo4j',
        'CouchDB', 'InfluxDB', 'ClickHouse', 'Snowflake', 'BigQuery', 'Redshift',
        'S3', 'MinIO', 'Hadoop', 'Spark', 'Hive', 'Presto', 'Trino', 'Databricks',
    ],
    'Cloud & Infrastructure': [
        'AWS', 'Amazon Web Services', 'Azure', 'Microsoft Azure', 'GCP', 'Google Cloud Platform',
        'Google Cloud', 'Heroku', 'DigitalOcean', 'Linode', 'Vercel', 'Netlify', 'Railway',
        'Render', 'Cloudflare', 'Terraform', 'Pulumi', 'CloudFormation', 'CDK',
        'Docker', 'Kubernetes', 'K8s', 'Helm', 'Istio', 'Linkerd', 'Consul', 'Vault',
        'Nomad', 'Ansible', 'Puppet', 'Chef', 'SaltStack',
    ],
    'DevOps & CI/CD': [
        'CI/CD', 'Jenkins', 'GitHub Actions', 'GitLab CI', 'CircleCI', 'Travis CI',
        'ArgoCD', 'Spinnaker', 'TeamCity', 'Bamboo', 'Drone CI', 'Buildkite',
        'Prometheus', 'Grafana', 'Datadog', 'New Relic', 'Sentry', 'ELK Stack',
        'Logstash', 'Kibana', 'Fluentd', 'Jaeger', 'OpenTelemetry',
    ],
    'Tools & Version Control': [
        'Git', 'GitHub', 'GitLab', 'Bitbucket', 'Subversion', 'Mercurial',
        'Jira', 'Confluence', 'Notion', 'Slack', 'Trello', 'Asana', 'Linear',
        'Postman', 'Insomnia', 'Swagger', 'OpenAPI', 'Figma', 'Sketch', 'Adobe XD',
        'VS Code', 'Vim', 'Neovim', 'IntelliJ', 'PyCharm', 'WebStorm', 'Eclipse',
        'Makefile', 'Gradle', 'Maven', 'Webpack', 'Vite', 'Rollup', 'ESBuild',
        'Yarn', 'npm', 'pnpm', 'pip', 'Conda', 'Poetry',
    ],
    'Soft Skills': [
        'Leadership', 'Communication', 'Teamwork', 'Problem Solving', 'Critical Thinking',
        'Time Management', 'Project Management', 'Agile', 'Scrum', 'Kanban',
        'Mentoring', 'Collaboration', 'Presentation', 'Public Speaking', 'Writing',
        'Analytical Skills', 'Decision Making', 'Conflict Resolution', 'Negotiation',
        'Adaptability', 'Creativity', 'Innovation', 'Strategic Planning',
        'Cross-functional', 'Stakeholder Management', 'Technical Writing',
    ],
    'Domains & Specializations': [
        'Machine Learning', 'Deep Learning', 'Natural Language Processing', 'NLP',
        'Computer Vision', 'Data Science', 'Data Engineering', 'Data Analysis',
        'Data Analytics', 'Business Intelligence', 'Artificial Intelligence', 'AI',
        'LLM', 'Large Language Model', 'DevOps', 'Site Reliability Engineering', 'SRE',
        'Cybersecurity', 'Security', 'Cloud Computing', 'Distributed Systems',
        'Microservices', 'System Design', 'Software Architecture', 'QA', 'Quality Assurance',
        'Testing', 'Mobile Development', 'Web Development', 'Full Stack', 'Frontend',
        'Backend', 'API Development', 'Database Administration', 'DBA', 'Network Engineering',
        'Blockchain', 'IoT', 'Embedded Systems', 'Game Development', 'AR/VR',
        'UI/UX Design', 'User Research', 'Product Management', 'Business Analysis',
    ],
    'Design & Creative': [
        'Figma', 'Sketch', 'Adobe XD', 'Photoshop', 'Illustrator', 'InDesign',
        'After Effects', 'Premiere Pro', 'Lightroom', 'Final Cut Pro', 'DaVinci Resolve',
        'Blender', 'Maya', '3ds Max', 'Cinema 4D', 'Unity', 'Unreal Engine',
        'Canva', 'Inkscape', 'GIMP', 'Krita', 'Procreate',
        'Typography', 'Color Theory', 'Wireframing', 'Prototyping', 'User Research',
        'Usability Testing', 'Design Systems', 'Responsive Design', 'Accessibility',
    ],
    'Data & Analytics': [
        'Tableau', 'Power BI', 'Looker', 'Metabase', 'Superset', 'Redash',
        'Excel', 'Google Sheets', 'VBA', 'SAS', 'SPSS', 'Stata',
        'Apache Spark', 'Apache Flink', 'Apache Beam', 'Airflow', 'dbt',
        'Jupyter', 'Jupyter Notebook', 'Colab', 'RStudio', 'KNIME', 'RapidMiner',
        'A/B Testing', 'Statistical Analysis', 'Regression', 'Classification',
        'Clustering', 'Time Series', 'Forecasting', 'Experimental Design',
    ],
    'Marketing & Sales': [
        'SEO', 'SEM', 'Google Ads', 'Facebook Ads', 'LinkedIn Ads', 'Content Marketing',
        'Social Media Marketing', 'Email Marketing', 'Marketing Automation',
        'HubSpot', 'Salesforce', 'Marketo', 'Mailchimp', 'SendGrid', 'Twilio',
        'Google Analytics', 'Google Tag Manager', 'Hotjar', 'Mixpanel', 'Amplitude',
        'CRM', 'Customer Success', 'Lead Generation', 'Copywriting', 'Branding',
        'Growth Hacking', 'Product Marketing', 'Market Research', 'A/B Testing',
    ],
    'Accounting & Finance': [
        'QuickBooks', 'Xero', 'Sage', 'Peachtree', 'Wave', 'FreshBooks',
        'Excel', 'Financial Modeling', 'Financial Analysis', 'Forecasting',
        'Budgeting', 'Auditing', 'Tax Preparation', 'Payroll', 'Bookkeeping',
        'GAAP', 'IFRS', 'CPA', 'CFA', 'ERP', 'SAP', 'Oracle Financials',
        'Accounts Payable', 'Accounts Receivable', 'Reconciliation',
    ],
    'Human Resources': [
        'Recruiting', 'Talent Acquisition', 'Onboarding', 'HRIS', 'BambooHR',
        'Workday', 'SuccessFactors', 'ADP', 'Paychex', 'Paycom',
        'Performance Management', 'Employee Relations', 'Compensation',
        'Benefits Administration', 'Training', 'L&D', 'Diversity & Inclusion',
        'Labor Law', 'Compliance', 'HR Policies', 'Workplace Investigations',
    ],
    'Project & Product Management': [
        'Agile', 'Scrum', 'Kanban', 'SAFe', 'Lean', 'Waterfall',
        'Jira', 'Confluence', 'Asana', 'Trello', 'Monday.com', 'ClickUp',
        'Basecamp', 'Notion', 'Smartsheet', 'Microsoft Project', 'Gantt',
        'Roadmapping', 'Sprint Planning', 'Retrospective', 'Stand-ups',
        'Product Strategy', 'Go-to-Market', 'User Stories', 'Acceptance Criteria',
        'Aha!', 'Productboard', 'Amplitude', 'Mixpanel',
    ],
    'Healthcare & Medical': [
        'HIPAA', 'HL7', 'FHIR', 'Epic', 'Cerner', 'Meditech', 'Allscripts',
        'Electronic Health Records', 'EHR', 'EMR', 'Medical Coding', 'CPT',
        'ICD-10', 'Patient Care', 'Clinical Research', 'Pharmaceutical',
        'Nursing', 'Medical Billing', 'Healthcare Compliance', 'Telemedicine',
    ],
}

PROFICIENCY_MAP = {
    'beginner': 25,
    'intermediate': 50,
    'advanced': 75,
    'expert': 100,
}

LEVEL_LABELS = {
    'beginner': 'Beginner',
    'intermediate': 'Intermediate',
    'advanced': 'Advanced',
    'expert': 'Expert',
}


def normalize_text(text):
    return re.sub(r'[^a-z0-9\s]', '', text.lower())


def tokenize(text):
    return set(normalize_text(text).split())


def extract_skills_from_jd(jd_text):
    found_skills = {}
    text_lower = jd_text.lower()

    for category, skills in SKILL_TAXONOMY.items():
        for skill in skills:
            skill_lower = skill.lower()
            score = 0

            if skill_lower in text_lower:
                score = len(skill_lower) / max(len(skill_lower), 1)
            else:
                skill_tokens = set(skill_lower.split())
                if len(skill_tokens) > 1 and skill_tokens.issubset(tokenize(jd_text)):
                    score = 0.8

            if score > 0:
                found_skills[skill] = {
                    'name': skill,
                    'category': category,
                    'confidence': round(score * 100, 1),
                }

    return found_skills


def get_resume_skill_map(resume):
    skills_data = {}
    for s in resume.skills.all():
        skills_data[s.name.lower()] = {
            'name': s.name,
            'level': s.proficiency_level,
            'level_score': PROFICIENCY_MAP.get(s.proficiency_level, 0),
        }
    return skills_data


def extract_skills_from_resume_text(text):
    found = {}
    text_lower = text.lower()
    for category, skills in SKILL_TAXONOMY.items():
        for skill in skills:
            skill_lower = skill.lower()
            if skill_lower in text_lower:
                found[skill] = {
                    'name': skill,
                    'category': category,
                    'level': 'intermediate',
                    'level_score': 50,
                }
            else:
                skill_tokens = set(skill_lower.split())
                if len(skill_tokens) > 1 and skill_tokens.issubset(tokenize(text)):
                    found[skill] = {
                        'name': skill,
                        'category': category,
                        'level': 'intermediate',
                        'level_score': 50,
                    }
    return found


def analyze_match_from_text(resume_text, job_text):
    resume_skills = extract_skills_from_resume_text(resume_text)
    jd_skills = extract_skills_from_jd(job_text)

    matched = []
    missing = []
    partial = []

    matched_count = 0
    total_score = 0
    total_possible = len(jd_skills) * 100 if jd_skills else 1

    for jd_skill_name, jd_skill_info in jd_skills.items():
        jd_lower = jd_skill_name.lower()
        best_match = None
        best_ratio = 0.0

        for rs_lower, rs_info in resume_skills.items():
            ratio = fuzzy_match_skill(rs_lower, jd_lower)
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = rs_info

        threshold = 0.6
        if best_match and best_ratio >= threshold:
            your_level = best_match['level_score']
            total_score += your_level
            matched_count += 1

            if your_level < 100:
                partial.append({
                    'name': jd_skill_name,
                    'category': jd_skill_info['category'],
                    'your_level': 'Detected',
                    'your_score': your_level,
                    'target_score': 100,
                    'suggested_upgrade': 'advanced',
                })
            else:
                matched.append({
                    'name': jd_skill_name,
                    'category': jd_skill_info['category'],
                    'your_level': 'Detected',
                    'your_score': your_level,
                })
        else:
            missing.append({
                'name': jd_skill_name,
                'category': jd_skill_info['category'],
                'your_level': 'Missing',
                'your_score': 0,
            })

    overall_score = round((total_score / total_possible) * 100, 1) if total_possible else 0
    recommendations = generate_recommendations(matched, missing, partial, overall_score)

    return {
        'overall_score': overall_score,
        'matched_skills': matched,
        'missing_skills': missing,
        'partial_skills': partial,
        'total_jd_skills': len(jd_skills),
        'matched_count': matched_count,
        'missing_count': len(missing),
        'partial_count': len(partial),
        'recommendations': recommendations,
    }


def fuzzy_match_skill(resume_skill_name, jd_skill_name):
    return SequenceMatcher(None, resume_skill_name.lower(), jd_skill_name.lower()).ratio()


def analyze_match(resume, job_text):
    jd_skills = extract_skills_from_jd(job_text)
    resume_skills = get_resume_skill_map(resume)

    matched = []
    missing = []
    partial = []

    matched_count = 0
    total_score = 0
    total_possible = len(jd_skills) * 100 if jd_skills else 1

    for jd_skill_name, jd_skill_info in jd_skills.items():
        jd_lower = jd_skill_name.lower()
        best_match = None
        best_ratio = 0.0

        for rs_lower, rs_info in resume_skills.items():
            ratio = fuzzy_match_skill(rs_lower, jd_lower)
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = rs_info

        threshold = 0.6
        if best_match and best_ratio >= threshold:
            your_level = best_match['level_score']
            score = your_level
            total_score += score
            matched_count += 1

            if your_level < 100:
                partial.append({
                    'name': jd_skill_name,
                    'category': jd_skill_info['category'],
                    'your_level': LEVEL_LABELS.get(best_match['level'], 'Unknown'),
                    'your_score': your_level,
                    'target_score': 100,
                    'suggested_upgrade': _suggest_upgrade(best_match['level']),
                })
            else:
                matched.append({
                    'name': jd_skill_name,
                    'category': jd_skill_info['category'],
                    'your_level': LEVEL_LABELS.get(best_match['level'], 'Unknown'),
                    'your_score': your_level,
                })
        else:
            total_score += 0
            missing.append({
                'name': jd_skill_name,
                'category': jd_skill_info['category'],
                'your_level': 'Missing',
                'your_score': 0,
            })

    overall_score = round((total_score / total_possible) * 100, 1) if total_possible else 0

    recommendations = generate_recommendations(matched, missing, partial, overall_score)

    return {
        'overall_score': overall_score,
        'matched_skills': matched,
        'missing_skills': missing,
        'partial_skills': partial,
        'total_jd_skills': len(jd_skills),
        'matched_count': matched_count,
        'missing_count': len(missing),
        'partial_count': len(partial),
        'recommendations': recommendations,
    }


def _suggest_upgrade(current_level):
    upgrades = {
        'beginner': 'intermediate',
        'intermediate': 'advanced',
        'advanced': 'expert',
    }
    return upgrades.get(current_level, 'expert')


def generate_recommendations(matched, missing, partial, overall_score):
    lines = []

    if overall_score >= 80:
        lines.append("Strong match! Your resume covers most of the required skills.")
    elif overall_score >= 60:
        lines.append("Good match! Some skill gaps exist that you should address.")
    elif overall_score >= 40:
        lines.append("Moderate match. Consider adding missing skills and upgrading proficiency levels.")
    else:
        lines.append("Low match. Your resume needs significant improvement to align with this role.")

    if missing:
        lines.append(f"\nMissing Skills ({len(missing)}):")
        categories = {}
        for s in missing:
            categories.setdefault(s['category'], []).append(s['name'])
        for cat, skills in sorted(categories.items()):
            lines.append(f"  \u2022 {cat}: {', '.join(skills[:5])}{'...' if len(skills) > 5 else ''}")

    if partial:
        lines.append(f"\nSkills to Upgrade ({len(partial)}):")
        for s in partial[:5]:
            lines.append(f"  \u2022 Upgrade '{s['name']}' from {s['your_level']} to {s['suggested_upgrade'].title()}")

    lines.append("\nTips:")
    lines.append("  \u2022 Add missing skills to your resume if you have experience with them")
    lines.append("  \u2022 Upgrade proficiency levels by adding more detailed descriptions of your work")
    lines.append("  \u2022 Tailor bullet points in your experience section to match JD keywords")
    lines.append("  \u2022 Use the exact terminology from the job description in your resume")

    return "\n".join(lines)
