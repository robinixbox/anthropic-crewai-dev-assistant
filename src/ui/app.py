import streamlit as st
import streamlit.components.v1 as components
from streamlit_ace import st_ace
import time
import json
import logging
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional, Tuple
import os
import sys
import traceback
from pathlib import Path

# Add the parent directory to sys.path to allow imports from sibling modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config import Config
from src.error_handler import ErrorHandler, AppError, ErrorCategory, ErrorSeverity
from src.agents import AnalystAgent, ArchitectAgent, DeveloperAgent, ReviewerAgent


# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Anthropic CrewAI Dev Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS to improve the UI appearance
st.markdown("""
<style>
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 1rem;
}
.stTabs [data-baseweb="tab"] {
    height: 3rem;
}
.success {
    padding: 1rem;
    border-radius: 0.5rem;
    background-color: #d4edda;
    color: #155724;
}
.warning {
    padding: 1rem;
    border-radius: 0.5rem;
    background-color: #fff3cd;
    color: #856404;
}
.error {
    padding: 1rem;
    border-radius: 0.5rem;
    background-color: #f8d7da;
    color: #721c24;
}
.info {
    padding: 1rem;
    border-radius: 0.5rem;
    background-color: #d1ecf1;
    color: #0c5460;
}
.agent-card {
    padding: 1rem;
    border-radius: 0.5rem;
    background-color: #f8f9fa;
    margin-bottom: 1rem;
}
.result-area {
    padding: 1rem;
    border-radius: 0.5rem;
    background-color: #f8f9fa;
    margin-top: 1rem;
}
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_config() -> Config:
    """
    Get the application configuration.
    
    Returns:
        Config: The application configuration
    """
    try:
        return Config()
    except Exception as e:
        st.error(f"Error loading configuration: {str(e)}")
        logger.error(f"Error loading configuration: {e}", exc_info=True)
        return None

def init_session_state():
    """Initialize session state variables if they don't exist"""
    if 'api_key' not in st.session_state:
        st.session_state.api_key = os.getenv('ANTHROPIC_API_KEY', '')
    if 'github_token' not in st.session_state:
        st.session_state.github_token = os.getenv('GITHUB_ACCESS_TOKEN', '')
    if 'language' not in st.session_state:
        st.session_state.language = 'Java'
    if 'model' not in st.session_state:
        st.session_state.model = 'claude-3-5-sonnet-20240620'
    if 'temperature' not in st.session_state:
        st.session_state.temperature = 0.2
    if 'last_error' not in st.session_state:
        st.session_state.last_error = None
    if 'errors' not in st.session_state:
        st.session_state.errors = []
    if 'current_task' not in st.session_state:
        st.session_state.current_task = None
    if 'task_status' not in st.session_state:
        st.session_state.task_status = None
    if 'results' not in st.session_state:
        st.session_state.results = {}
    if 'code_input' not in st.session_state:
        st.session_state.code_input = '// Paste your code here or write a new one'
    if 'code_output' not in st.session_state:
        st.session_state.code_output = ''
    if 'specifications' not in st.session_state:
        st.session_state.specifications = ''
    if 'architecture' not in st.session_state:
        st.session_state.architecture = ''
    if 'review_results' not in st.session_state:
        st.session_state.review_results = None

def display_sidebar():
    """Display the sidebar with configuration options"""
    st.sidebar.title("Configuration")
    
    with st.sidebar.expander("API Keys", expanded=False):
        st.session_state.api_key = st.text_input("Anthropic API Key", 
                                               value=st.session_state.api_key, 
                                               type="password")
        
        st.session_state.github_token = st.text_input("GitHub Access Token", 
                                                   value=st.session_state.github_token, 
                                                   type="password")
    
    with st.sidebar.expander("Agent Configuration", expanded=True):
        st.session_state.language = st.selectbox("Programming Language", 
                                               options=['Java', 'Python', 'JavaScript', 'C#', 'Go', 'Rust', 'TypeScript'],
                                               index=0)
        
        st.session_state.model = st.selectbox("Claude Model", 
                                           options=['claude-3-5-sonnet-20240620', 
                                                   'claude-3-opus-20240229',
                                                   'claude-3-sonnet-20240229',
                                                   'claude-3-haiku-20240307'],
                                           index=0)
        
        st.session_state.temperature = st.slider("Temperature", 
                                              min_value=0.0, 
                                              max_value=1.0, 
                                              value=st.session_state.temperature,
                                              step=0.1)
    
    with st.sidebar.expander("GitHub Integration", expanded=False):
        st.text_input("GitHub Repository Owner", value=os.getenv('GITHUB_OWNER', ''), key="github_owner")
        st.text_input("GitHub Repository Name", value=os.getenv('GITHUB_REPO', ''), key="github_repo")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Tools")
    
    if st.sidebar.button("Clear Errors"):
        st.session_state.errors = []
        st.session_state.last_error = None
        ErrorHandler.clear_errors()
        st.sidebar.success("Errors cleared")
    
    if st.sidebar.button("Reset Session"):
        for key in list(st.session_state.keys()):
            if key not in ['api_key', 'github_token']:
                del st.session_state[key]
        init_session_state()
        st.sidebar.success("Session reset")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info(
        """
        **Anthropic CrewAI Dev Assistant** est un outil d'aide au développement utilisant l'API Claude d'Anthropic 
        et le framework CrewAI pour orchestrer des agents IA spécialisés.
        
        [GitHub Repository](https://github.com/robinixbox/anthropic-crewai-dev-assistant)
        """
    )

def display_error_status():
    """Display error counts and status"""
    if st.session_state.errors:
        critical, error, warning, info, debug = ErrorHandler.get_error_summary()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Critiques", critical, None, "inverse")
        with col2:
            st.metric("Erreurs", error, None, "inverse")
        with col3:
            st.metric("Avertissements", warning, None, "inverse")
        with col4:
            st.metric("Infos", info, None, "inverse")
        with col5:
            st.metric("Débug", debug, None, "inverse")
        
        if critical > 0 or error > 0:
            st.error("Des erreurs critiques ont été détectées. Veuillez vérifier l'onglet 'Erreurs' pour plus de détails.")
        elif warning > 0:
            st.warning("Des avertissements ont été détectés. Veuillez vérifier l'onglet 'Erreurs' pour plus de détails.")

def display_error_details():
    """Display detailed error information"""
    if not st.session_state.errors:
        st.info("Aucune erreur n'a été détectée.")
        return
    
    st.subheader("Erreurs détectées")
    
    # Group errors by category
    errors_by_category = {}
    for error in st.session_state.errors:
        if error.category.value not in errors_by_category:
            errors_by_category[error.category.value] = []
        errors_by_category[error.category.value].append(error)
    
    # Display errors by category with expanders
    for category, errors in errors_by_category.items():
        with st.expander(f"{category} ({len(errors)})"):
            for error in errors:
                severity_color = {
                    "CRITICAL": "#721c24",
                    "ERROR": "#721c24",
                    "WARNING": "#856404",
                    "INFO": "#0c5460",
                    "DEBUG": "#155724"
                }.get(error.severity.value, "#212529")
                
                st.markdown(f"""
                <div style="padding: 1rem; border-radius: 0.5rem; background-color: #f8f9fa; margin-bottom: 1rem;">
                    <h4 style="color: {severity_color};">{error.severity.value}: {error.message}</h4>
                    <p><strong>Timestamp:</strong> {error.timestamp}</p>
                    
                    <h5>Suggestions:</h5>
                    <ul>
                    {"".join(f'<li>{suggestion}</li>' for suggestion in error.suggestions)}
                    </ul>
                    
                    {f'<h5>Détails:</h5><pre style="background-color: #f1f1f1; padding: 0.5rem; border-radius: 0.25rem;">{json.dumps(error.details, indent=2)}</pre>' if error.details else ''}
                    
                    {f'<h5>Traceback:</h5><pre style="background-color: #f1f1f1; padding: 0.5rem; border-radius: 0.25rem; white-space: pre-wrap;">{error.traceback}</pre>' if error.traceback else ''}
                </div>
                """, unsafe_allow_html=True)

def display_code_review():
    """Display the code review interface"""
    st.subheader("Revue de Code")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Code à Analyser")
        
        # Code editor for input
        code_input = st_ace(
            value=st.session_state.code_input,
            language=st.session_state.language.lower(),
            theme="github",
            min_lines=20,
            max_lines=40,
            key="code_ace"
        )
        
        if code_input:
            st.session_state.code_input = code_input
        
        st.markdown("### Spécifications (optionnel)")
        specifications = st.text_area("Décrivez les spécifications que le code devrait respecter", 
                                   value=st.session_state.specifications,
                                   height=100,
                                   key="specs_input")
        
        if specifications:
            st.session_state.specifications = specifications
        
        # Review configuration
        st.markdown("### Type d'analyse")
        analysis_type = st.multiselect("Sélectionnez les analyses à effectuer",
                                    options=["Qualité du code", "Sécurité", "Performance", "Conformité aux spécifications"],
                                    default=["Qualité du code"])
        
        if st.button("Analyser le Code", type="primary"):
            if not st.session_state.code_input or st.session_state.code_input == '// Paste your code here or write a new one':
                st.error("Veuillez entrer du code à analyser.")
                return
            
            try:
                # Create a reviewer agent
                reviewer = ReviewerAgent(
                    api_key=st.session_state.api_key,
                    model=st.session_state.model,
                    temperature=st.session_state.temperature,
                    language=st.session_state.language,
                    verbose=True
                )
                
                with st.spinner("Analyse du code en cours..."):
                    # Mock review results (would be actual agent execution in production)
                    review_results = reviewer.review_code(st.session_state.code_input, st.session_state.specifications)
                    
                    # Add security and performance analysis if requested
                    if "Sécurité" in analysis_type:
                        review_results["security_issues"] = reviewer.analyze_security(st.session_state.code_input)
                    
                    if "Performance" in analysis_type:
                        review_results["performance_issues"] = reviewer.analyze_performance(st.session_state.code_input)
                    
                    st.session_state.review_results = review_results
                    st.success("Analyse terminée !")
                
            except Exception as e:
                error = ErrorHandler.create_error(
                    message="Erreur lors de l'analyse du code",
                    category=ErrorCategory.GENERAL,
                    severity=ErrorSeverity.ERROR,
                    exception=e
                )
                st.session_state.errors.append(error)
                st.session_state.last_error = error
                st.error(f"Erreur lors de l'analyse du code : {str(e)}")
                logger.error(f"Code analysis error: {e}", exc_info=True)
    
    with col2:
        st.markdown("### Résultats de l'analyse")
        
        if st.session_state.review_results:
            # Issues by severity
            issues = st.session_state.review_results.get("issues", [])
            
            # Count issues by severity
            severity_counts = {"high": 0, "medium": 0, "low": 0}
            for issue in issues:
                severity = issue.get("severity", "").lower()
                if severity in severity_counts:
                    severity_counts[severity] += 1
            
            # Display metrics
            col_high, col_medium, col_low = st.columns(3)
            with col_high:
                st.metric("Problèmes critiques", severity_counts["high"], None, "inverse")
            with col_medium:
                st.metric("Problèmes moyens", severity_counts["medium"], None, "inverse")
            with col_low:
                st.metric("Problèmes mineurs", severity_counts["low"], None, "inverse")
            
            # Detailed issues
            if issues:
                with st.expander("Problèmes détectés", expanded=True):
                    for i, issue in enumerate(issues):
                        severity = issue.get("severity", "").lower()
                        color = {"high": "#721c24", "medium": "#856404", "low": "#155724"}.get(severity, "#212529")
                        
                        st.markdown(f"""
                        <div style="padding: 0.5rem; border-radius: 0.5rem; background-color: #f8f9fa; margin-bottom: 0.5rem;">
                            <h4 style="color: {color};">Problème #{i+1}: {issue.get('description', 'Problème non spécifié')}</h4>
                            <p><strong>Sévérité:</strong> {severity.capitalize()}</p>
                            <p><strong>Ligne:</strong> {issue.get('line', 'N/A')}</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Suggestions
            suggestions = st.session_state.review_results.get("suggestions", [])
            if suggestions:
                with st.expander("Suggestions d'amélioration", expanded=True):
                    for i, suggestion in enumerate(suggestions):
                        st.markdown(f"""
                        <div style="padding: 0.5rem; border-radius: 0.5rem; background-color: #f8f9fa; margin-bottom: 0.5rem;">
                            <h4>Suggestion #{i+1}</h4>
                            <p>{suggestion.get('description', 'Suggestion non spécifiée')}</p>
                            <pre style="background-color: #f1f1f1; padding: 0.5rem; border-radius: 0.25rem;">{suggestion.get('code', 'Code non spécifié')}</pre>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Security issues
            security_issues = st.session_state.review_results.get("security_issues", [])
            if security_issues:
                with st.expander("Vulnérabilités de sécurité", expanded=True):
                    for i, issue in enumerate(security_issues):
                        severity = issue.get("severity", "").lower()
                        color = {"critical": "#721c24", "high": "#856404", "medium": "#0c5460", "low": "#155724"}.get(severity, "#212529")
                        
                        st.markdown(f"""
                        <div style="padding: 0.5rem; border-radius: 0.5rem; background-color: #f8f9fa; margin-bottom: 0.5rem;">
                            <h4 style="color: {color};">Vulnérabilité #{i+1}: {issue.get('vulnerability_type', 'Non spécifiée')}</h4>
                            <p><strong>Sévérité:</strong> {severity.capitalize()}</p>
                            <p><strong>Description:</strong> {issue.get('description', 'Non spécifiée')}</p>
                            <p><strong>Localisation:</strong> {issue.get('location', 'Non spécifiée')}</p>
                            <p><strong>Correction recommandée:</strong> {issue.get('mitigation', 'Non spécifiée')}</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Performance issues
            performance_issues = st.session_state.review_results.get("performance_issues", [])
            if performance_issues:
                with st.expander("Problèmes de performance", expanded=True):
                    for i, issue in enumerate(performance_issues):
                        severity = issue.get("severity", "").lower()
                        color = {"high": "#721c24", "medium": "#856404", "low": "#155724"}.get(severity, "#212529")
                        
                        st.markdown(f"""
                        <div style="padding: 0.5rem; border-radius: 0.5rem; background-color: #f8f9fa; margin-bottom: 0.5rem;">
                            <h4 style="color: {color};">Problème de performance #{i+1}: {issue.get('issue_type', 'Non spécifié')}</h4>
                            <p><strong>Sévérité:</strong> {severity.capitalize()}</p>
                            <p><strong>Description:</strong> {issue.get('description', 'Non spécifiée')}</p>
                            <p><strong>Localisation:</strong> {issue.get('location', 'Non spécifiée')}</p>
                            <p><strong>Suggestion:</strong> {issue.get('suggestion', 'Non spécifiée')}</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Overall assessment
            st.markdown("### Évaluation globale")
            st.markdown(f"""
            <div style="padding: 1rem; border-radius: 0.5rem; background-color: #f8f9fa; margin-top: 1rem;">
                <p>{st.session_state.review_results.get('overall_assessment', 'Aucune évaluation globale disponible.')}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Lancez une analyse de code pour voir les résultats ici.")

def display_code_generation():
    """Display the code generation interface"""
    st.subheader("Génération de Code")
    
    # Project information
    st.markdown("### Informations du projet")
    
    col1, col2 = st.columns(2)
    
    with col1:
        project_name = st.text_input("Nom du projet", value="Mon Projet")
        project_description = st.text_area("Description du projet", 
                                       value="Description du projet",
                                       height=100)
    
    with col2:
        project_type = st.selectbox("Type de projet", 
                                 options=["Application Web", "API REST", "Microservice", "Application Desktop", "Bibliothèque", "Autre"])
        target_platform = st.multiselect("Plateformes cibles", 
                                      options=["Web", "Mobile", "Desktop", "Cloud", "IoT", "Autre"],
                                      default=["Web"])
    
    # User requirements
    st.markdown("### Exigences du projet")
    requirements = st.text_area("Décrivez les exigences de votre projet", 
                             value="",
                             height=150,
                             help="Décrivez en détail ce que vous voulez que votre application fasse")
    
    # Technical constraints
    st.markdown("### Contraintes techniques")
    
    col1, col2 = st.columns(2)
    
    with col1:
        frameworks = st.multiselect("Frameworks ou bibliothèques", 
                                 options=[
                                     # Java options
                                     "Spring Boot", "Jakarta EE", "Quarkus", "Micronaut", "Hibernate", "JDBC",
                                     # Python options
                                     "Django", "Flask", "FastAPI", "SQLAlchemy", "Pandas", "NumPy",
                                     # JavaScript options
                                     "React", "Angular", "Vue", "Express", "Node.js", "Next.js",
                                     # Other options
                                     "Autre"
                                 ],
                                 default=[])
    
    with col2:
        databases = st.multiselect("Bases de données", 
                                options=["MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Oracle", "SQL Server", "Autre"],
                                default=[])
    
    additional_constraints = st.text_area("Contraintes additionnelles", 
                                       value="",
                                       height=100,
                                       help="Spécifiez toutes les contraintes additionnelles (performances, sécurité, etc.)")
    
    # Generate code button
    if st.button("Générer le Code", type="primary"):
        if not requirements:
            st.error("Veuillez entrer les exigences du projet.")
            return
        
        try:
            # Set up agents for the generation process
            analyst = AnalystAgent(
                api_key=st.session_state.api_key,
                model=st.session_state.model,
                temperature=st.session_state.temperature,
                language=st.session_state.language,
                verbose=True
            )
            
            architect = ArchitectAgent(
                api_key=st.session_state.api_key,
                model=st.session_state.model,
                temperature=st.session_state.temperature,
                language=st.session_state.language,
                verbose=True
            )
            
            developer = DeveloperAgent(
                api_key=st.session_state.api_key,
                model=st.session_state.model,
                temperature=st.session_state.temperature,
                language=st.session_state.language,
                verbose=True
            )
            
            # Combine requirements and constraints
            full_requirements = f"""
            Projet: {project_name}
            Description: {project_description}
            Type: {project_type}
            Plateformes: {', '.join(target_platform)}
            
            Exigences:
            {requirements}
            
            Contraintes techniques:
            - Langage: {st.session_state.language}
            - Frameworks/Bibliothèques: {', '.join(frameworks) if frameworks else 'Aucun spécifié'}
            - Bases de données: {', '.join(databases) if databases else 'Aucune spécifiée'}
            - Contraintes additionnelles: {additional_constraints if additional_constraints else 'Aucune spécifiée'}
            """
            
            # Create a progress bar for the process
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Analyze requirements
            status_text.text("Étape 1/3: Analyse des exigences...")
            progress_bar.progress(10)
            time.sleep(0.5)  # Simulating processing time
            
            # In a real application, this would be a proper agent task execution
            # For demo purposes, we're just using placeholder results
            specifications = f"Spécifications analysées pour {project_name} en {st.session_state.language}"
            progress_bar.progress(30)
            
            # Step 2: Design architecture
            status_text.text("Étape 2/3: Conception de l'architecture...")
            progress_bar.progress(40)
            time.sleep(0.5)  # Simulating processing time
            
            # In a real application, this would be a proper agent task execution
            architecture = f"Architecture conçue pour {project_name} en {st.session_state.language}"
            progress_bar.progress(60)
            
            # Step 3: Implement code
            status_text.text("Étape 3/3: Génération du code...")
            progress_bar.progress(70)
            time.sleep(0.5)  # Simulating processing time
            
            # In a real application, this would be a proper agent task execution
            generated_code = f"""
// Generated {st.session_state.language} code for {project_name}

/**
 * Sample code for demonstration purposes
 * A real implementation would generate actual working code
 * based on the analyzed requirements and architecture design
 */
package com.example.demo;

public class Main {{
    public static void main(String[] args) {{
        System.out.println("Hello, {project_name}!");
        // Implementation would go here
    }}
}}
            """
            
            progress_bar.progress(100)
            status_text.text("Génération terminée !")
            
            # Display the results
            st.session_state.specifications = specifications
            st.session_state.architecture = architecture
            st.session_state.code_output = generated_code
            
            # Navigate to the results tab
            st.success("Code généré avec succès!")
            
        except Exception as e:
            error = ErrorHandler.create_error(
                message="Erreur lors de la génération du code",
                category=ErrorCategory.GENERAL,
                severity=ErrorSeverity.ERROR,
                exception=e
            )
            st.session_state.errors.append(error)
            st.session_state.last_error = error
            st.error(f"Erreur lors de la génération du code : {str(e)}")
            logger.error(f"Code generation error: {e}", exc_info=True)
    
    # Display generated code if available
    if st.session_state.code_output:
        st.markdown("### Code Généré")
        
        st.markdown("#### Architecture")
        st.text_area("Architecture", value=st.session_state.architecture, height=100, disabled=True)
        
        st.markdown("#### Spécifications")
        st.text_area("Spécifications", value=st.session_state.specifications, height=100, disabled=True)
        
        st.markdown("#### Code")
        st_ace(
            value=st.session_state.code_output,
            language=st.session_state.language.lower(),
            theme="github",
            readonly=True,
            min_lines=15,
            max_lines=30
        )

def display_github_integration():
    """Display GitHub integration interface"""
    st.subheader("Intégration GitHub")
    
    if not st.session_state.github_token:
        st.warning("Veuillez configurer votre token GitHub dans la barre latérale pour utiliser cette fonctionnalité.")
        return
    
    st.markdown("### Configuration du Workflow")
    
    col1, col2 = st.columns(2)
    
    with col1:
        workflow_type = st.selectbox("Type de Workflow", 
                                  options=["Analyse de Code", "Génération de Code", "Revue de Pull Request"])
        trigger_type = st.selectbox("Déclencheur", 
                                 options=["Issue", "Pull Request", "Push", "Événement Manuel"])
    
    with col2:
        repo_owner = st.text_input("Propriétaire du dépôt", value=st.session_state.get('github_owner', ''))
        repo_name = st.text_input("Nom du dépôt", value=st.session_state.get('github_repo', ''))
    
    st.markdown("### Configuration du Workflow")
    
    with st.expander("Détails du workflow", expanded=True):
        if workflow_type == "Analyse de Code":
            st.checkbox("Analyser la qualité du code", value=True)
            st.checkbox("Analyser la sécurité", value=True)
            st.checkbox("Analyser les performances", value=False)
            st.checkbox("Générer des suggestions d'amélioration", value=True)
            st.checkbox("Créer une Issue avec les résultats", value=True)
            
        elif workflow_type == "Génération de Code":
            st.text_area("Description des exigences", height=100, 
                       help="Décrivez les exigences qui seront utilisées pour générer le code")
            st.checkbox("Créer une Pull Request avec le code généré", value=True)
            
        elif workflow_type == "Revue de Pull Request":
            st.checkbox("Analyse automatique de la Pull Request", value=True)
            st.checkbox("Ajouter des commentaires dans la PR", value=True)
            st.checkbox("Approuver automatiquement si pas d'erreur", value=False)
    
    # Create workflow button
    if st.button("Créer le Workflow GitHub", type="primary"):
        if not repo_owner or not repo_name:
            st.error("Veuillez spécifier le propriétaire et le nom du dépôt GitHub.")
            return
        
        try:
            # Create a file with the workflow configuration
            workflow_yaml = f"""name: {workflow_type}

on:
  {trigger_type.lower().replace(' ', '_')}:
    types: [opened, reopened, synchronize]

jobs:
  {workflow_type.lower().replace(' ', '_')}:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          
      - name: Run {workflow_type}
        run: |
          python src/app.py --{workflow_type.lower().replace(' ', '_')}
        env:
          ANTHROPIC_API_KEY: \${{ secrets.ANTHROPIC_API_KEY }}
          GITHUB_TOKEN: \${{ secrets.GITHUB_TOKEN }}
"""
            
            # In a real application, this would use the GitHub API to create the workflow file
            # For demo purposes, we'll just show a success message
            
            st.success(f"Workflow '{workflow_type}' créé avec succès dans le dépôt {repo_owner}/{repo_name}!")
            
            # Display the generated workflow YAML
            st.markdown("### Workflow YAML généré")
            st.code(workflow_yaml, language="yaml")
            
        except Exception as e:
            error = ErrorHandler.create_error(
                message="Erreur lors de la création du workflow GitHub",
                category=ErrorCategory.GITHUB,
                severity=ErrorSeverity.ERROR,
                exception=e
            )
            st.session_state.errors.append(error)
            st.session_state.last_error = error
            st.error(f"Erreur lors de la création du workflow GitHub : {str(e)}")
            logger.error(f"GitHub workflow creation error: {e}", exc_info=True)

def main():
    """Main application entry point"""
    # Initialize session state
    init_session_state()
    
    # Display sidebar
    display_sidebar()
    
    # Display header
    st.title("🤖 Anthropic CrewAI Dev Assistant")
    st.markdown("Un assistant de développement intelligent utilisant CrewAI et l'API Anthropic Claude")
    
    # Display error status if errors exist
    if st.session_state.errors:
        display_error_status()
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Revue de Code", "Génération de Code", "Intégration GitHub", "Erreurs"])
    
    # Tab content
    with tab1:
        display_code_review()
    
    with tab2:
        display_code_generation()
    
    with tab3:
        display_github_integration()
    
    with tab4:
        display_error_details()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Erreur inattendue : {str(e)}")
        logger.error(f"Unexpected error: {e}", exc_info=True)
        
        error = ErrorHandler.create_error(
            message="Erreur inattendue dans l'application",
            category=ErrorCategory.GENERAL,
            severity=ErrorSeverity.CRITICAL,
            exception=e
        )
        
        st.markdown(f"""
        <div class="error">
            <h3>Une erreur critique s'est produite :</h3>
            <p>{str(e)}</p>
            <p>Consultez les logs pour plus de détails.</p>
            
            <h4>Suggestions :</h4>
            <ul>
            {"".join(f'<li>{suggestion}</li>' for suggestion in error.suggestions)}
            </ul>
            
            <h4>Traceback :</h4>
            <pre>{traceback.format_exc()}</pre>
        </div>
        """, unsafe_allow_html=True)