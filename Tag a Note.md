## How to Tag a Note

You can tag notes in your Smart Notes application through both the **frontend UI** and **API calls**. Here's how:

### Frontend (UI) Method

1. **Create a New Note with Tags**:
   - Click "Create Note" button
   - Fill in title and content
   - Use the **Tag Selector** component to:
     - Select existing tags from the dropdown
     - Create new tags by typing a name and clicking the "+" button
   - Save the note

2. **Edit Existing Note Tags**:
   - Click on an existing note to edit it
   - Modify the selected tags using the Tag Selector
   - Save changes

### API Method

**Create a note with tags:**
```bash
POST /api/notes/
{
  "title": "My Note",
  "content": "Note content here",
  "tag_ids": [1, 2, 3],  // Array of tag IDs
  "auto_summarize": true
}
```

**Update note tags:**
```bash
PATCH /api/notes/{note_id}/
{
  "tag_ids": [1, 2, 3]  // Replace existing tags
}
```

### Tag Management

**Create a new tag:**
```bash
POST /api/tags/
{
  "name": "important"
}
```

**List all your tags:**
```bash
GET /api/tags/
```

**Filter notes by tag:**
```bash
GET /api/notes/?tag=1
```

### Key Points

- **Many-to-Many Relationship**: Notes can have multiple tags, and tags can be used on multiple notes
- **User-Scoped**: Tags are private to each user
- **Unique Names**: Tag names must be unique per user
- **Auto-Creation**: The frontend allows creating tags on-the-fly when creating notes
- **Optional**: Tagging is optional - you can create notes without any tags

The system automatically handles the relationship between notes and tags, and you can filter/search notes by tags in the UI.