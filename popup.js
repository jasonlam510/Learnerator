document.addEventListener('DOMContentLoaded', function() {
    const topicInput = document.getElementById('topicInput');
    const generateBtn = document.getElementById('generateBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const timelineContainer = document.getElementById('timelineContainer');
    const inputSection = document.getElementById('inputSection');
    const learningHeader = document.getElementById('learningHeader');
    const learningTopic = document.getElementById('learningTopic');
    const timeline = document.getElementById('timeline');

    // API Configuration
    const API_BASE_URL = 'http://localhost:3000/api';

    // Dummy data for testing - React learning plan
    const dummyLearningPlan = [
        {
            header: "1. JavaScript Fundamentals",
            details: "Master ES6+ features, async/await, promises, and modern JavaScript concepts. Focus on arrow functions, destructuring, and modules. Practice with real-world examples and build small projects to reinforce your understanding.",
            status: "finished"
        },
        {
            header: "2. HTML & CSS Basics",
            details: "Learn semantic HTML, CSS Grid, Flexbox, and responsive design principles. Understand the box model and CSS selectors. Create responsive layouts and understand modern CSS techniques.",
            status: "finished"
        },
        {
            header: "3. React Core Concepts",
            details: "Understand JSX, components, props, state, and the component lifecycle. Learn about functional components and hooks. Build simple components and understand React's declarative nature.",
            status: "ongoing"
        },
        {
            header: "4. State Management",
            details: "Master useState, useEffect, useContext, and custom hooks. Learn about state lifting and prop drilling patterns. Implement complex state management solutions and understand when to use different approaches.",
            status: "pending"
        },
        {
            header: "5. Advanced React Patterns",
            details: "Explore higher-order components, render props, compound components, and performance optimization techniques. Learn about React.memo, useMemo, and useCallback for performance optimization.",
            status: "pending"
        },
        {
            header: "6. Routing & Navigation",
            details: "Implement client-side routing with React Router, handle dynamic routes, and manage navigation state. Learn about route guards, nested routes, and programmatic navigation.",
            status: "pending"
        },
        {
            header: "7. API Integration",
            details: "Learn to fetch data from APIs, handle loading states, error boundaries, and implement data fetching patterns. Understand RESTful APIs, GraphQL, and modern data fetching libraries like React Query.",
            status: "pending"
        },
        {
            header: "8. Testing React Applications",
            details: "Write unit tests with Jest and React Testing Library, test user interactions, and implement integration tests. Learn about testing best practices, mocking, and test-driven development.",
            status: "pending"
        },
        {
            header: "9. Build & Deploy",
            details: "Set up build tools, optimize bundle size, deploy to platforms like Vercel or Netlify, and implement CI/CD. Learn about webpack, code splitting, and performance optimization techniques.",
            status: "pending"
        },
        {
            header: "10. Advanced Topics",
            details: "Explore TypeScript integration, server-side rendering, code splitting, and advanced performance techniques. Learn about Next.js, Gatsby, and other React frameworks.",
            status: "pending"
        }
    ];

    // Function to check if backend is available
    async function checkBackendHealth() {
        try {
            const response = await fetch(`${API_BASE_URL}/health`);
            return response.ok;
        } catch (error) {
            console.log('Backend not available, using dummy data');
            return false;
        }
    }

    // Function to get learning plan from backend
    async function getLearningPlanFromBackend(topic) {
        try {
            const response = await fetch(`${API_BASE_URL}/learning-plans/${encodeURIComponent(topic)}`);
            if (response.ok) {
                const data = await response.json();
                return data.stages.map(stage => ({
                    header: stage.header,
                    details: stage.details,
                    status: stage.status
                }));
            }
            return null;
        } catch (error) {
            console.error('Error fetching from backend:', error);
            return null;
        }
    }

    // Function to save learning plan to backend
    async function saveLearningPlanToBackend(topic, learningPlan) {
        try {
            const response = await fetch(`${API_BASE_URL}/learning-plans`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    topic: topic,
                    stages: learningPlan
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('Learning plan saved to backend:', data);
                return true;
            } else {
                console.error('Failed to save learning plan:', response.statusText);
                return false;
            }
        } catch (error) {
            console.error('Error saving to backend:', error);
            return false;
        }
    }

    // Function to call LLM server (TODO for user to implement)
    async function callLLMServer(topic) {
        // First, check if backend is available
        const backendAvailable = await checkBackendHealth();
        
        if (backendAvailable) {
            // Try to get existing plan from backend
            const existingPlan = await getLearningPlanFromBackend(topic);
            if (existingPlan) {
                console.log('Found existing plan in backend');
                return existingPlan;
            }
        }
        
        // TODO: Replace this with actual LLM server call
        // Example implementation:
        /*
        try {
            const response = await fetch('YOUR_LLM_SERVER_ENDPOINT', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer YOUR_API_KEY'
                },
                body: JSON.stringify({
                    topic: topic,
                    prompt: `Generate a comprehensive learning plan for ${topic} with 8-10 stages. Each stage should have a header and detailed description with multiple sentences separated by periods.`
                })
            });
            
            const data = await response.json();
            const learningPlan = data.learningPlan;
            
            // Save to backend if available
            if (backendAvailable) {
                await saveLearningPlanToBackend(topic, learningPlan);
            }
            
            return learningPlan;
        } catch (error) {
            console.error('Error calling LLM server:', error);
            throw error;
        }
        */
        
        // For now, return dummy data
        console.log('Using dummy data for topic:', topic);
        const learningPlan = dummyLearningPlan;
        
        // Save to backend if available
        if (backendAvailable) {
            await saveLearningPlanToBackend(topic, learningPlan);
        }
        
        return learningPlan;
    }

    // Function to format details into bullet points
    function formatDetails(details) {
        // Split by periods and filter out empty strings
        const sentences = details.split('.').map(s => s.trim()).filter(s => s.length > 0);
        
        // Create bullet points from sentences
        return sentences.map(sentence => sentence.charAt(0).toUpperCase() + sentence.slice(1));
    }

    // Function to show learning header
    function showLearningHeader(topic) {
        // Hide input section and logo header
        inputSection.classList.add('hidden');
        document.querySelector('.logo-header').classList.add('hidden');
        
        // Set the topic text
        learningTopic.textContent = topic;
        
        // Show learning header
        learningHeader.style.display = 'block';
    }

    // Function to render timeline
    function renderTimeline(learningPlan) {
        timeline.innerHTML = '';

        learningPlan.forEach((stage, index) => {
            const timelineItem = document.createElement('div');
            timelineItem.className = `timeline-item ${stage.status}`;

            const dot = document.createElement('div');
            dot.className = `timeline-dot ${stage.status}`;

            // Create header container
            const header = document.createElement('div');
            header.className = 'timeline-header';
            header.textContent = stage.header;

            // Create details container with bullet points
            const details = document.createElement('div');
            details.className = 'timeline-details';

            const bulletPoints = formatDetails(stage.details);
            const ul = document.createElement('ul');
            
            bulletPoints.forEach(point => {
                const li = document.createElement('li');
                li.textContent = point;
                ul.appendChild(li);
            });

            details.appendChild(ul);

            // Assemble the timeline item
            timelineItem.appendChild(dot);
            timelineItem.appendChild(header);
            timelineItem.appendChild(details);
            timeline.appendChild(timelineItem);
        });
    }

    // Handle generate button click
    generateBtn.addEventListener('click', async function() {
        const topic = topicInput.value.trim();
        
        if (!topic) {
            alert('Please enter a topic to learn!');
            return;
        }

        // Show loading state
        generateBtn.disabled = true;
        loadingSpinner.style.display = 'block';
        timelineContainer.style.display = 'none';

        try {
            // Call LLM server to get learning plan
            const learningPlan = await callLLMServer(topic);
            
            // Hide loading and show learning header
            loadingSpinner.style.display = 'none';
            showLearningHeader(topic);
            
            // Render the timeline
            renderTimeline(learningPlan);
            
            // Show timeline
            timelineContainer.style.display = 'block';
        } catch (error) {
            console.error('Error generating learning plan:', error);
            alert('Error generating learning plan. Please try again.');
        } finally {
            // Re-enable button
            generateBtn.disabled = false;
        }
    });

    // Handle Enter key press
    topicInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            generateBtn.click();
        }
    });

    // Focus on input when popup opens
    topicInput.focus();
}); 