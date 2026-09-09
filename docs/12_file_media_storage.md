# 12 — File & Media Storage

## Decision

The project will support **images only** for property media. We will not support property videos for the MVP.

## Why

Property images are an important part of the marketplace, but storing large binary files directly in PostgreSQL is unnecessary for this project.

PostgreSQL remains the source of truth for structured application data, while file/object storage holds the actual image files.

## Storage Model

```text
User uploads image
        ↓
   Django backend
        ↓
 Validate image
        ↓
   File storage
        ↓
 Image URL/path
        ↓
 PostgreSQL property_media
```

The `property_media` table stores metadata such as:

- `property_id`
- `url`
- `media_type`
- `is_primary`
- `created_at`

The actual image bytes are stored outside PostgreSQL.

## Development

During development, use Django's local media storage:

```text
Django
  ↓
media/
  ├── properties/
  └── users/
```

This keeps local development simple.

## Production

For production, use object/file storage rather than storing uploaded files on the application server.

The exact provider will be decided later. An S3-compatible object-storage service is a suitable direction.

The application should continue to work with a storage abstraction so changing the provider does not require rewriting property/business logic.

## Upload Flow

```text
Client
  ↓
GraphQL mutation
  ↓
Django
  ↓
Validate file
  ↓
Store image
  ↓
Create property_media record
  ↓
Return image information
```

Validation should cover at least:

- Allowed image types
- File size limits
- Basic upload security
- Reasonable image dimensions where appropriate

## Image Processing

Image resizing/compression can be added later.

If processing becomes expensive, it should run through Celery rather than blocking the main request.

```text
Upload
  ↓
Store original
  ↓
Return success
  ↓
Celery
  ↓
Resize/compress/optimize
```

This is optional for the first version.

## Media Scope

### MVP

- Property images
- Primary property image
- Multiple images per property
- Upload/delete images
- Store image URLs/metadata in PostgreSQL

### Not in MVP

- Property videos
- Video streaming
- Video transcoding
- Large media processing pipelines
- CDN architecture beyond what the chosen object-storage provider naturally provides

## Important Rules

1. Do not store image binaries directly in PostgreSQL.
2. PostgreSQL stores image metadata and references.
3. Validate uploaded files before accepting them.
4. Keep file storage separate from business logic.
5. Use local storage during development.
6. Use object storage in production.
7. Do not introduce complicated media infrastructure unless the project actually needs it.

## Final Architecture

```text
                    Django
                       │
              ┌────────┴────────┐
              ↓                 ↓
         PostgreSQL        File Storage
              │                 │
        Media metadata      Image files
              │                 │
              └───────┬─────────┘
                      ↓
                 Image URL
                      ↓
                   Client
```
