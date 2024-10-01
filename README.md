# Social Media API

## Project Overview

This project is a **Social Media API** built using Django and Django REST Framework. The API allows users to create, read, update, and delete posts, follow other users, and view a feed of posts from the users they follow. The goal of this project is to simulate a real-world social media platform while focusing on core backend development concepts like user management, database interactions, and CRUD operations.

## Features

- **Post Management**: Users can create, update, delete, and retrieve posts. Each post contains content (text), an optional media URL (image), and a timestamp.
- **User Management**: Users can create an account, update their profile, and view other users' profiles.
- **Follow System**: Users can follow or unfollow other users.
- **Feed of Posts**: Users can view a feed of posts from the users they follow, ordered by the most recent posts.
- **Authentication**: The API uses Django's authentication system to protect routes for creating, updating, and deleting posts.

## Technologies

- **Django**: Web framework for rapid development.
- **Django REST Framework (DRF)**: Toolkit for building Web APIs.
- **SQLite**: Default database for development (can be swapped with PostgreSQL/MySQL in production).
- **Git**: Version control.
- **GitHub**: Remote repository to track changes.

## Installation

### Prerequisites

- Python 3.x
- Pip
- Virtual Environment

### Setup Instructions

1. Clone the repository:

   ```bash
   git clone https://github.com/ivanjumingx/social_media_api.git
   cd social_media_api
   ```

2. Create a virtual environment:

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations to set up the database:

   ```bash
   python manage.py migrate
   ```

5. Run the development server:

   ```bash
   python manage.py runserver
   ```

6. Access the API at `http://127.0.0.1:8000/`.

## Usage

- API documentation will be added here as the project progresses.

## Endpoints

- `GET /posts/`: Retrieve a list of posts.
- `POST /posts/`: Create a new post (requires authentication).
- `PUT /posts/<id>/`: Update a post (only the author can update).
- `DELETE /posts/<id>/`: Delete a post (only the author can delete).
- `POST /follow/<user_id>/`: Follow a user.
- `GET /feed/`: View the feed of posts from followed users.

## Roadmap

### Week 1

- Set up project structure
- Implement CRUD for posts and users
- Set up the follower system

### Week 2

- Add user authentication and permissions
- Implement the feed of posts
- Add error handling, testing, and pagination
- Deploy the project to Heroku

### Stretch Goals

- Add comments, likes, and notifications.
- Implement direct messaging between users.
- Allow media uploads to posts.

## License

This project is open source and available under the MIT License (<https://opensource.org/licenses/MIT>).

### Key Sections Explained

1. **Project Overview**: A short summary of what the project is about and its primary goals.
2. **Features**: Highlights the main functionality the API offers.
3. **Technologies**: Lists the main technologies and tools used in the project.
4. **Installation**: A step-by-step guide to getting the project set up on a local machine.
5. **Usage**: Instructions on how to interact with the API (you'll fill this in more as you build the API).
6. **Endpoints**: A quick reference for key API endpoints (add more as you implement).
7. **Roadmap**: A timeline to show what has been completed and what will be worked on next.
8. **License**: The open-source license for your project (optional but useful if you plan to share the code).
