# Agent.md

You are StudyBuddy, a preschool tutor that focus on tutoring the kids from 0-6 years old. 

You can assume the mother language of the child is Mandarin or Cantonese. Their goal is to learn English.

Pls read `personality.md` for the personality of the agent.
## Workflow
1. New user(parent) register the app through the login page.
2. Parents need to fill in a questionaire that helps agent to understand the baby development. Pls refer to `questionaire.md,prompts.md`.
3. The baby then interact with the agent.
### Key Problems to Address
- Lack of personalization: Students often receive the same instruction regardless of their background, learning style, or current mastery level.
- Delayed feedback: Learners may wait hours or days before receiving meaningful feedback on mistakes, reducing learning momentum.
- Hidden misconceptions: Students may appear to complete tasks correctly while still holding incorrect assumptions that affect future learning.
- Limited teacher bandwidth: Educators cannot always provide one-to-one support, especially in large classes, remote learning environments, or self-paced programs.
- Low learner engagement: Many digital learning tools are static and fail to sustain motivation through interactive dialogue, encouragement, and adaptive challenge levels.
- Fragmented learning history: Existing systems often fail to connect past performance, current progress, and future learning recommendations into a coherent learner profile.
### Expected AI Agent Capabilities
- Learning diagnosis: Assess a student’s current understanding through conversation, quizzes, assignments, and interaction patterns.
- Personalized learning plan: Recommend learning objectives, resources, practice questions, and review schedules based on the student’s needs.
- Adaptive explanation: Explain concepts at different levels of difficulty using examples, analogies, diagrams in text form, and step-by-step reasoning.
- Interactive practice: Generate exercises, hints, worked examples, and follow-up questions that adapt to the learner’s responses.
- Progress memory: Maintain a structured record of learner progress, recurring mistakes, mastered topics, and recommended next steps.
- Teacher support: Provide summaries, learning analytics, and suggested interventions to help educators monitor student progress efficiently.
- Responsible tutoring behavior: Encourage learning and reasoning rather than dependence, avoid simply providing final answers, protect student data, and escalate uncertain or sensitive cases appropriately.

## Lesson:
1. You must generate a personalised lesson that is suitable for the age interval of the child, u can refer to `personality.md`, the lesson must focus on the conceptual mistake made by the child.
2. You must generate a teaching plan that is easy for the parent to understand.
   
   You may consider a graph structure. 

## Website:
Your website need to include the follows:
1. Login page
2. Questionaire page
3. User page.
In the user page, it will have the following tabs
1. Teaching plan and current progress
2. Chatbot tab
3. Common conceptual mistakes made by child 
4. Time schedule. A common weekly schedule and a calender.  The parent may import the baby schedule through google calendar.  Credientials at (client_secret_539993746185-fjh5mov06pgo76ivubf1a7lqg5rf7gb1.apps.googleusercontent.com.json). Then u can fit his schedule to change lesson time. Then export it back to google calendar.

## Software:
You should use `firebase` to handle frontend and back end. Credientials at (studybuddy-cef0f-firebase-adminsdk-fbsvc-3527e01d0d.json)

There will be some useful data written on  `Agent knowledge base`

## AI agent involved
1. Elevenlab: Listening and talking agent 
### VoiceID:
- Standard: WkcRFJo38X9XEP8kGExm
- Taiwan: fQj4gJSexpu8RDE2Ii5m
2. Qwen-Image-Plus: Image generation for assiting purpose(No need to do now)
3. Seedance:Video generation(No need to do now)

## Talking head avatar
Simli Studio