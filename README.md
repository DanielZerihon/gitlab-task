# GitLab API Integration Service

A Flask-based REST API service that provides simplified endpoints for common GitLab operations, including user role management and data retrieval.

## 📋 Overview

This service wraps the GitLab API to provide two main functionalities:

1. **Set User Role** - Grant or update user permissions on GitLab repositories or groups
2. **Get Data** - Retrieve issues or merge requests filtered by year

## 🚀 Installation & Running

### Run with Docker

1. **Build the Docker image:**
   ```bash
   cd gitlab-task/
   docker build -t gitlab-api-service .
   ```
2. **Edit the .env file**
   ```
   GITLAB_URL=http://host.docker.internal
   GITLAB_TOKEN=<insert_your_token_here>
   ```
3. **Run the container:**
   ```bash
   docker run \
   -p 5000:5000 \
   --env-file .env \
   --name gitlab-api \
   gitlab-api-service
   ```

## 📖 API Documentation

### 1. Set User Role

Grant or update permissions for a user on a GitLab repository or group.

**Role Access Levels:**
| Role | Access Level | Permissions |
|------|--------------|-------------|
| Guest | 10 | View issues, leave comments |
| Reporter | 20 | Pull code, create issues |
| Developer | 30 | Push to non-protected branches, merge |
| Maintainer | 40 | Manage project settings, push to protected branches |
| Owner | 50 | Full control (groups only) |

**Example Request:**
```bash
  curl -X POST http://localhost:5000/set-role \
   -H "Content-Type: application/json" \
   -d '{"username": "daniel_zerihon", "repo_or_group": "gpt/many_groups_and_projects/gpt-subgroup-6/gpt-project-26", "role": "Owner"}'
```
### 2. Get Data

Retrieve issues or merge requests created during a specific year.

**Fetch all merge from 2017:**
```bash
curl "http://localhost:5000/get-data?type=mr&year=2017"
```

**Fetch all issues requests from 2017:**
```bash
curl "http://localhost:5000/get-data?type=issues&year=2017"
```
