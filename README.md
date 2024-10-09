# Restaurant Search API

This project is a Restaurant Search API that allows users to query a database of restaurants based on certain parameters such as cuisine type, kosher status, and opening hours. It also includes an admin interface for managing restaurants and viewing an audit log of queries.

## Table of Contents
- [Application Overview](#application-overview)
- [Database](#database)
- [Infrastructure](#infrastructure)
- [Setup and Deployment](#setup-and-deployment)
- [API Endpoints](#api-endpoints)
- [Admin Interface](#admin-interface)
- [Assumptions](#assumptions)

## Application Overview
The "Restaurant Search API" is implemented using Python, Flask, and SQLAlchemy, with SQLite as the database. It allows users to:
- Search restaurants based on various parameters.
- View if restaurants are kosher.
- Check if restaurants are currently open.
- Use an admin page to add, edit, or delete restaurants.
- View an audit log of the searches performed within the last 24 hours.

## Database
The application uses SQLite as the database. SQLite is provisioned locally in the `restaurants.db` file, which is configured through AWS Secrets Manager. The secrets are managed using Terraform.

The `Restaurant` table consists of the following columns:
- `id`: Integer (Primary Key)
- `name`: String (Restaurant name)
- `address`: String
- `phone`: String
- `website`: String
- `opening_hours`: String
- `cuisine_type`: String
- `is_kosher`: Boolean

The `AuditLog` table stores information about the queries performed:
- `id`: Integer (Primary Key)
- `query`: String (The query parameters used)
- `ip`: String (IP address of the requester)
- `country`: String (Country of the requester)
- `timestamp`: DateTime (The time when the query was performed)

## Infrastructure
The infrastructure for the application is defined and provisioned using Terraform. It includes:
- **AWS EC2 Instance**: Hosting the application.
- **AWS Secrets Manager**: Storing sensitive configuration values like the `SECRET_KEY`, `SQLALCHEMY_DATABASE_URI`, and `ADMIN_PASSWORD`.

## Assumptions
- The SQLite database is stored locally on the EC2 instance and is not designed for production-grade, high-scale scenarios.
- The EC2 instance provisions a local SQLite database (`restaurants.db`) which can be updated or queried via API or the admin page.
- Sensitive data such as `SECRET_KEY`, database URI, and `ADMIN_PASSWORD` are managed using AWS Secrets Manager.
- The application assumes an AWS region of `us-east-1` unless otherwise specified.

## Notes for Examiner
- The `SQLALCHEMY_DATABASE_URI` is set to use SQLite for simplicity (`sqlite:///restaurants.db`). This is suitable for testing and development purposes. For production, it would be preferable to use a managed relational database service (such as AWS RDS).
- The SQLite database is provisioned locally on the EC2 instance, which means this setup is not highly available. It is recommended to transition to a managed, replicated database for resilience.
