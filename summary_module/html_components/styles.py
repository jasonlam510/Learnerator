"""
Styles Generator for Learning Dashboard

Generates comprehensive CSS styles for all dashboard components
including responsive design, animations, and theme support.
"""


class StylesGenerator:
    """Generates CSS styles for the learning dashboard."""
    
    def generate_all_styles(self) -> str:
        """Generate complete CSS stylesheet for the dashboard."""
        
        base_styles = self._generate_base_styles()
        layout_styles = self._generate_layout_styles()
        component_styles = self._generate_component_styles()
        knowledge_map_styles = self._generate_knowledge_map_styles()
        quiz_styles = self._generate_quiz_styles()
        navigation_styles = self._generate_navigation_styles()
        responsive_styles = self._generate_responsive_styles()
        animation_styles = self._generate_animation_styles()
        
        return f"""
        {base_styles}
        {layout_styles}
        {component_styles}
        {knowledge_map_styles}
        {quiz_styles}
        {navigation_styles}
        {responsive_styles}
        {animation_styles}
        """
    
    def _generate_base_styles(self) -> str:
        """Generate base styles and CSS variables."""
        
        return """
        /* Base Styles and CSS Variables */
        :root {
            /* Colors */
            --primary-color: #2563eb;
            --secondary-color: #7c3aed;
            --accent-color: #059669;
            --warning-color: #d97706;
            --error-color: #dc2626;
            --success-color: #16a34a;
            
            /* Neutral Colors */
            --gray-50: #f9fafb;
            --gray-100: #f3f4f6;
            --gray-200: #e5e7eb;
            --gray-300: #d1d5db;
            --gray-400: #9ca3af;
            --gray-500: #6b7280;
            --gray-600: #4b5563;
            --gray-700: #374151;
            --gray-800: #1f2937;
            --gray-900: #111827;
            
            /* Topic Colors */
            --python-color: #3776ab;
            --frontend-color: #61dafb;
            --devops-color: #326ce5;
            --datascience-color: #ff6b35;
            --database-color: #336791;
            --general-color: var(--gray-600);
            --web-color: #e34c26;
            --mobile-color: #a4c639;
            --ai-color: #ff6f00;
            --backend-color: #68217a;
            
            /* Spacing */
            --spacing-xs: 0.25rem;
            --spacing-sm: 0.5rem;
            --spacing-md: 1rem;
            --spacing-lg: 1.5rem;
            --spacing-xl: 2rem;
            --spacing-2xl: 3rem;
            
            /* Typography */
            --font-family-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            --font-family-mono: 'Fira Code', 'Monaco', 'Cascadia Code', monospace;
            
            /* Border Radius */
            --radius-sm: 0.375rem;
            --radius-md: 0.5rem;
            --radius-lg: 0.75rem;
            --radius-xl: 1rem;
            
            /* Shadows */
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
            --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        html {
            font-size: 16px;
            line-height: 1.5;
        }
        
        body {
            font-family: var(--font-family-sans);
            background: linear-gradient(135deg, var(--gray-50) 0%, var(--gray-100) 100%);
            color: var(--gray-800);
            min-height: 100vh;
        }
        
        /* Scrollbar Styling */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--gray-100);
            border-radius: var(--radius-md);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--gray-300);
            border-radius: var(--radius-md);
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--gray-400);
        }
        """
    
    def _generate_layout_styles(self) -> str:
        """Generate layout and container styles."""
        
        return """
        /* Layout Styles */
        .dashboard-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: var(--spacing-md);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .dashboard-header {
            background: white;
            border-radius: var(--radius-xl);
            padding: var(--spacing-xl);
            margin-bottom: var(--spacing-lg);
            box-shadow: var(--shadow-md);
            text-align: center;
        }
        
        .dashboard-header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: var(--spacing-sm);
        }
        
        .subtitle {
            font-size: 1.125rem;
            color: var(--gray-600);
            margin-bottom: var(--spacing-lg);
        }
        
        .stats {
            display: flex;
            justify-content: center;
            gap: var(--spacing-xl);
            flex-wrap: wrap;
        }
        
        .stat {
            background: var(--gray-50);
            padding: var(--spacing-sm) var(--spacing-md);
            border-radius: var(--radius-md);
            font-weight: 600;
            color: var(--gray-700);
        }
        
        .dashboard-nav {
            background: white;
            border-radius: var(--radius-lg);
            margin-bottom: var(--spacing-lg);
            box-shadow: var(--shadow-sm);
            overflow: hidden;
        }
        
        .dashboard-nav ul {
            display: flex;
            list-style: none;
            margin: 0;
            padding: 0;
        }
        
        .dashboard-nav li {
            flex: 1;
        }
        
        .dashboard-nav a {
            display: block;
            padding: var(--spacing-md) var(--spacing-lg);
            text-decoration: none;
            color: var(--gray-600);
            font-weight: 500;
            text-align: center;
            transition: all 0.2s ease;
            border-right: 1px solid var(--gray-200);
        }
        
        .dashboard-nav a:hover {
            background: var(--gray-50);
            color: var(--primary-color);
        }
        
        .dashboard-nav a.active {
            background: var(--primary-color);
            color: white;
        }
        
        .dashboard-nav li:last-child a {
            border-right: none;
        }
        
        .dashboard-main {
            flex: 1;
            background: white;
            border-radius: var(--radius-xl);
            padding: var(--spacing-xl);
            box-shadow: var(--shadow-md);
            margin-bottom: var(--spacing-lg);
        }
        
        .content-section {
            animation: fadeIn 0.3s ease-in-out;
        }
        
        .content-section h2 {
            font-size: 2rem;
            font-weight: 700;
            color: var(--gray-800);
            margin-bottom: var(--spacing-md);
        }
        
        .section-description {
            font-size: 1.125rem;
            color: var(--gray-600);
            margin-bottom: var(--spacing-xl);
            line-height: 1.6;
        }
        
        .dashboard-footer {
            text-align: center;
            padding: var(--spacing-lg);
            color: var(--gray-500);
            font-size: 0.875rem;
        }
        
        .dashboard-footer a {
            color: var(--primary-color);
            text-decoration: none;
        }
        
        .dashboard-footer a:hover {
            text-decoration: underline;
        }
        """
    
    def _generate_component_styles(self) -> str:
        """Generate styles for reusable components."""
        
        return """
        /* Component Styles */
        .content-card {
            background: white;
            border-radius: var(--radius-lg);
            padding: var(--spacing-lg);
            margin-bottom: var(--spacing-lg);
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--gray-200);
            transition: all 0.2s ease;
        }
        
        .content-card:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: var(--spacing-md);
        }
        
        .card-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--gray-800);
            margin-bottom: var(--spacing-xs);
        }
        
        .card-subtitle {
            font-size: 0.875rem;
            color: var(--gray-500);
            margin-bottom: var(--spacing-sm);
        }
        
        .card-type-badge {
            background: var(--primary-color);
            color: white;
            padding: var(--spacing-xs) var(--spacing-sm);
            border-radius: var(--radius-sm);
            font-size: 0.75rem;
            font-weight: 500;
            text-transform: uppercase;
        }
        
        .card-content {
            margin-bottom: var(--spacing-md);
        }
        
        .card-footer {
            border-top: 1px solid var(--gray-200);
            padding-top: var(--spacing-md);
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.875rem;
            color: var(--gray-500);
        }
        
        .tag {
            display: inline-block;
            background: var(--gray-100);
            color: var(--gray-700);
            padding: var(--spacing-xs) var(--spacing-sm);
            border-radius: var(--radius-sm);
            font-size: 0.75rem;
            font-weight: 500;
            margin-right: var(--spacing-xs);
            margin-bottom: var(--spacing-xs);
        }
        
        .tag.python-color { background: #3776ab20; color: var(--python-color); }
        .tag.frontend-color { background: #61dafb20; color: #1a8aa3; }
        .tag.devops-color { background: #326ce520; color: var(--devops-color); }
        .tag.datascience-color { background: #ff6b3520; color: var(--datascience-color); }
        .tag.database-color { background: #33679120; color: var(--database-color); }
        
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: var(--spacing-sm) var(--spacing-md);
            border: none;
            border-radius: var(--radius-md);
            font-size: 0.875rem;
            font-weight: 500;
            text-decoration: none;
            cursor: pointer;
            transition: all 0.2s ease;
            gap: var(--spacing-xs);
        }
        
        .btn-primary {
            background: var(--primary-color);
            color: white;
        }
        
        .btn-primary:hover {
            background: #1d4ed8;
            transform: translateY(-1px);
        }
        
        .btn-secondary {
            background: var(--gray-200);
            color: var(--gray-700);
        }
        
        .btn-secondary:hover {
            background: var(--gray-300);
        }
        
        .btn-outline {
            background: transparent;
            color: var(--primary-color);
            border: 1px solid var(--primary-color);
        }
        
        .btn-outline:hover {
            background: var(--primary-color);
            color: white;
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .btn:disabled:hover {
            transform: none;
        }
        """
    
    def _generate_knowledge_map_styles(self) -> str:
        """Generate styles for the knowledge map visualization."""
        
        return """
        /* Knowledge Map Styles */
        .knowledge-map-container {
            background: var(--gray-50);
            border-radius: var(--radius-lg);
            padding: var(--spacing-lg);
            margin-bottom: var(--spacing-lg);
        }
        
        .knowledge-map {
            width: 100%;
            height: 600px;
            border: 1px solid var(--gray-200);
            border-radius: var(--radius-md);
            background: white;
            position: relative;
            overflow: hidden;
        }
        
        .map-controls {
            position: absolute;
            top: var(--spacing-md);
            right: var(--spacing-md);
            display: flex;
            gap: var(--spacing-sm);
            z-index: 10;
        }
        
        .map-control-btn {
            background: white;
            border: 1px solid var(--gray-300);
            border-radius: var(--radius-sm);
            padding: var(--spacing-sm);
            cursor: pointer;
            box-shadow: var(--shadow-sm);
            transition: all 0.2s ease;
        }
        
        .map-control-btn:hover {
            background: var(--gray-50);
            box-shadow: var(--shadow-md);
        }
        
        .knowledge-node {
            fill: var(--primary-color);
            stroke: white;
            stroke-width: 2px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .knowledge-node:hover {
            fill: var(--secondary-color);
            stroke-width: 3px;
        }
        
        .knowledge-node.highlighted {
            fill: var(--accent-color);
            stroke: var(--warning-color);
            stroke-width: 4px;
        }
        
        .knowledge-link {
            stroke: var(--gray-400);
            stroke-width: 2px;
            stroke-opacity: 0.6;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .knowledge-link:hover {
            stroke: var(--primary-color);
            stroke-width: 3px;
            stroke-opacity: 0.8;
        }
        
        .knowledge-link.highlighted {
            stroke: var(--accent-color);
            stroke-width: 4px;
            stroke-opacity: 1;
        }
        
        .node-label {
            font-family: var(--font-family-sans);
            font-size: 12px;
            font-weight: 600;
            fill: var(--gray-700);
            text-anchor: middle;
            pointer-events: none;
            user-select: none;
        }
        
        .map-tooltip {
            position: absolute;
            background: var(--gray-800);
            color: white;
            padding: var(--spacing-sm) var(--spacing-md);
            border-radius: var(--radius-md);
            font-size: 0.875rem;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s ease;
            z-index: 100;
            max-width: 300px;
            box-shadow: var(--shadow-lg);
        }
        
        .map-tooltip.visible {
            opacity: 1;
        }
        
        .map-legend {
            position: absolute;
            bottom: var(--spacing-md);
            left: var(--spacing-md);
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: var(--radius-md);
            padding: var(--spacing-md);
            font-size: 0.75rem;
            box-shadow: var(--shadow-sm);
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: var(--spacing-sm);
            margin-bottom: var(--spacing-xs);
        }
        
        .legend-item:last-child {
            margin-bottom: 0;
        }
        
        .legend-color {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }
        """
    
    def _generate_quiz_styles(self) -> str:
        """Generate styles for the quiz interface."""
        
        return """
        /* Quiz Styles */
        .quiz-container {
            max-width: 800px;
            margin: 0 auto;
        }
        
        .quiz-header {
            text-align: center;
            margin-bottom: var(--spacing-xl);
            padding: var(--spacing-lg);
            background: var(--gray-50);
            border-radius: var(--radius-lg);
        }
        
        .quiz-header h3 {
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--gray-800);
            margin-bottom: var(--spacing-md);
        }
        
        .quiz-description {
            font-size: 1.125rem;
            color: var(--gray-600);
            margin-bottom: var(--spacing-lg);
            line-height: 1.6;
        }
        
        .quiz-meta {
            display: flex;
            justify-content: center;
            gap: var(--spacing-lg);
            flex-wrap: wrap;
            font-size: 0.875rem;
            color: var(--gray-600);
        }
        
        .quiz-progress {
            margin-bottom: var(--spacing-xl);
        }
        
        .progress-info {
            text-align: center;
            margin-bottom: var(--spacing-sm);
            font-weight: 600;
            color: var(--gray-700);
        }
        
        .progress-bar {
            height: 8px;
            background: var(--gray-200);
            border-radius: var(--radius-sm);
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
            transition: width 0.3s ease;
        }
        
        .quiz-question {
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: var(--radius-lg);
            padding: var(--spacing-xl);
            margin-bottom: var(--spacing-lg);
            box-shadow: var(--shadow-sm);
        }
        
        .question-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--spacing-md);
        }
        
        .question-header h4 {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--gray-800);
        }
        
        .question-concept {
            background: var(--primary-color);
            color: white;
            padding: var(--spacing-xs) var(--spacing-sm);
            border-radius: var(--radius-sm);
            font-size: 0.75rem;
            font-weight: 500;
        }
        
        .question-text {
            margin-bottom: var(--spacing-lg);
        }
        
        .question-text p {
            font-size: 1.125rem;
            line-height: 1.6;
            color: var(--gray-800);
        }
        
        .question-options {
            margin-bottom: var(--spacing-lg);
        }
        
        .option-label {
            display: flex;
            align-items: flex-start;
            gap: var(--spacing-md);
            padding: var(--spacing-md);
            border: 2px solid var(--gray-200);
            border-radius: var(--radius-md);
            margin-bottom: var(--spacing-sm);
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .option-label:hover {
            border-color: var(--primary-color);
            background: var(--gray-50);
        }
        
        .option-label:has(input:checked) {
            border-color: var(--primary-color);
            background: #2563eb10;
        }
        
        .option-label input[type="radio"] {
            margin-top: 2px;
        }
        
        .option-text {
            flex: 1;
            line-height: 1.5;
            color: var(--gray-700);
        }
        
        .question-source {
            font-size: 0.875rem;
            color: var(--gray-500);
            border-top: 1px solid var(--gray-200);
            padding-top: var(--spacing-md);
        }
        
        .question-source a {
            color: var(--primary-color);
            text-decoration: none;
        }
        
        .question-source a:hover {
            text-decoration: underline;
        }
        """
    
    def _generate_navigation_styles(self) -> str:
        """Generate styles for navigation and overview components."""
        
        return """
        /* Navigation and Overview Styles */
        .overview-container {
            animation: fadeIn 0.5s ease-in-out;
        }
        
        .welcome-section {
            text-align: center;
            margin-bottom: var(--spacing-2xl);
        }
        
        .welcome-section h2 {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--gray-800);
            margin-bottom: var(--spacing-md);
        }
        
        .welcome-text {
            font-size: 1.125rem;
            color: var(--gray-600);
            max-width: 600px;
            margin: 0 auto;
            line-height: 1.6;
        }
        
        .stats-overview {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--spacing-lg);
            margin-bottom: var(--spacing-2xl);
        }
        
        .stat-card {
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: var(--radius-lg);
            padding: var(--spacing-lg);
            text-align: center;
            box-shadow: var(--shadow-sm);
            transition: all 0.2s ease;
        }
        
        .stat-card:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }
        
        .stat-icon {
            font-size: 2rem;
            margin-bottom: var(--spacing-md);
        }
        
        .stat-content h3 {
            font-size: 2rem;
            font-weight: 700;
            color: var(--gray-800);
            margin-bottom: var(--spacing-xs);
        }
        
        .stat-content p {
            color: var(--gray-600);
            font-weight: 500;
        }
        """
    
    def _generate_responsive_styles(self) -> str:
        """Generate responsive styles for mobile and tablet devices."""
        
        return """
        /* Responsive Styles */
        @media (max-width: 768px) {
            .dashboard-container {
                padding: var(--spacing-sm);
            }
            
            .dashboard-header {
                padding: var(--spacing-lg);
            }
            
            .dashboard-header h1 {
                font-size: 2rem;
            }
            
            .stats {
                gap: var(--spacing-md);
            }
            
            .stat {
                font-size: 0.875rem;
                padding: var(--spacing-xs) var(--spacing-sm);
            }
            
            .dashboard-nav ul {
                flex-direction: column;
            }
            
            .dashboard-nav a {
                border-right: none;
                border-bottom: 1px solid var(--gray-200);
            }
            
            .dashboard-nav li:last-child a {
                border-bottom: none;
            }
            
            .dashboard-main {
                padding: var(--spacing-md);
            }
            
            .content-section h2 {
                font-size: 1.5rem;
            }
            
            .section-description {
                font-size: 1rem;
            }
            
            .stats-overview {
                grid-template-columns: repeat(2, 1fr);
                gap: var(--spacing-md);
            }
            
            .quiz-container {
                margin: 0;
            }
            
            .quiz-header {
                padding: var(--spacing-md);
            }
            
            .quiz-header h3 {
                font-size: 1.5rem;
            }
            
            .quiz-meta {
                flex-direction: column;
                gap: var(--spacing-sm);
            }
            
            .quiz-question {
                padding: var(--spacing-md);
            }
            
            .question-header {
                flex-direction: column;
                align-items: flex-start;
                gap: var(--spacing-sm);
            }
            
            .knowledge-map {
                height: 400px;
            }
            
            .map-controls {
                position: static;
                justify-content: center;
                margin-bottom: var(--spacing-md);
            }
            
            .map-legend {
                position: static;
                margin-top: var(--spacing-md);
            }
        }
        
        @media (max-width: 480px) {
            .stats-overview {
                grid-template-columns: 1fr;
            }
            
            .quiz-header h3 {
                font-size: 1.25rem;
            }
            
            .question-text p {
                font-size: 1rem;
            }
            
            .option-label {
                padding: var(--spacing-sm);
            }
            
            .knowledge-map {
                height: 300px;
            }
        }
        """
    
    def _generate_animation_styles(self) -> str:
        """Generate animation and transition styles."""
        
        return """
        /* Animation Styles */
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes pulse {
            0%, 100% {
                opacity: 1;
            }
            50% {
                opacity: 0.5;
            }
        }
        
        .animate-fadeIn {
            animation: fadeIn 0.5s ease-in-out;
        }
        
        .animate-slideIn {
            animation: slideIn 0.3s ease-out;
        }
        
        .animate-pulse {
            animation: pulse 2s infinite;
        }
        
        /* Loading states */
        .loading {
            position: relative;
            overflow: hidden;
        }
        
        .loading::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
            animation: loading 1.5s infinite;
        }
        
        @keyframes loading {
            0% {
                left: -100%;
            }
            100% {
                left: 100%;
            }
        }
        
        /* Hover effects */
        .hover-lift {
            transition: transform 0.2s ease;
        }
        
        .hover-lift:hover {
            transform: translateY(-4px);
        }
        
        .hover-scale {
            transition: transform 0.2s ease;
        }
        
        .hover-scale:hover {
            transform: scale(1.05);
        }
        
        /* Focus states */
        .focus-visible:focus {
            outline: 2px solid var(--primary-color);
            outline-offset: 2px;
        }
        
        /* Reduced motion */
        @media (prefers-reduced-motion: reduce) {
            *,
            *::before,
            *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }
        """
