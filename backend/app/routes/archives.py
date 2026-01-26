from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models import Archive, ArchiveCreate, ArchiveUpdate
from datetime import datetime

router = APIRouter()

# Mock database - replace with actual database implementation
mock_archives = [
    {
        "id": 1,
        "title": "Historical Records 1900-1920",
        "description": "Collection of municipal records from early 20th century Barcelona",
        "category": "Municipal",
        "date": "1900-1920",
        "created_at": datetime.now()
    },
    {
        "id": 2,
        "title": "Architectural Plans",
        "description": "Original architectural drawings of Gothic Quarter buildings",
        "category": "Architecture",
        "date": "1850-1900",
        "created_at": datetime.now()
    },
    {
        "id": 3,
        "title": "Civil Registry Documents",
        "description": "Birth, marriage, and death certificates from 1920-1950",
        "category": "Civil Registry",
        "date": "1920-1950",
        "created_at": datetime.now()
    },
    {
        "id": 4,
        "title": "Trade Union Records",
        "description": "Documents from Barcelona trade unions during industrialization",
        "category": "Labor",
        "date": "1880-1930",
        "created_at": datetime.now()
    },
    {
        "id": 5,
        "title": "Photography Collection",
        "description": "Historical photographs of Barcelona streets and monuments",
        "category": "Photography",
        "date": "1920-1960",
        "created_at": datetime.now()
    }
]

@router.get("/archives", response_model=List[Archive])
async def get_archives(
    search: Optional[str] = Query(None, description="Search term for archives"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """
    Get all archives with optional search and filtering
    """
    results = mock_archives.copy()
    
    if search:
        search_lower = search.lower()
        results = [
            archive for archive in results
            if search_lower in archive["title"].lower() 
            or search_lower in archive["description"].lower()
        ]
    
    if category:
        results = [
            archive for archive in results
            if archive["category"].lower() == category.lower()
        ]
    
    return results

@router.get("/archives/{archive_id}", response_model=Archive)
async def get_archive(archive_id: int):
    """
    Get a specific archive by ID
    """
    archive = next((a for a in mock_archives if a["id"] == archive_id), None)
    if not archive:
        raise HTTPException(status_code=404, detail="Archive not found")
    return archive

@router.post("/archives", response_model=Archive, status_code=201)
async def create_archive(archive: ArchiveCreate):
    """
    Create a new archive entry
    """
    new_id = max([a["id"] for a in mock_archives]) + 1 if mock_archives else 1
    new_archive = {
        "id": new_id,
        **archive.model_dump(),
        "created_at": datetime.now()
    }
    mock_archives.append(new_archive)
    return new_archive

@router.put("/archives/{archive_id}", response_model=Archive)
async def update_archive(archive_id: int, archive_update: ArchiveUpdate):
    """
    Update an existing archive
    """
    archive = next((a for a in mock_archives if a["id"] == archive_id), None)
    if not archive:
        raise HTTPException(status_code=404, detail="Archive not found")
    
    update_data = archive_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        archive[key] = value
    
    return archive

@router.delete("/archives/{archive_id}", status_code=204)
async def delete_archive(archive_id: int):
    """
    Delete an archive
    """
    global mock_archives
    archive = next((a for a in mock_archives if a["id"] == archive_id), None)
    if not archive:
        raise HTTPException(status_code=404, detail="Archive not found")
    
    mock_archives = [a for a in mock_archives if a["id"] != archive_id]
    return None

@router.get("/categories")
async def get_categories():
    """
    Get all unique categories
    """
    categories = list(set(archive["category"] for archive in mock_archives))
    return {"categories": sorted(categories)}
