# MapConfig

MapConfig is a simple, lightweight Python library for creating beautiful interactive maps using only place names (for example, "New Delhi", "Paris", "Tokyo") without needing to know coordinates.

It uses OpenStreetMap's Nominatim API to fetch coordinates and Folium to render maps.

---

## ⭐ Features

- 🔥 Add simple markers with just a place name
- 📍 Add circles to highlight areas
- 🖼️ Add custom icon markers
- 💨 Automatically center and display in the browser (no saving needed)
- 🌐 Show directly in a popup browser tab or export as HTML
- add paths between two places
- 
more coming soon .. 

---

## 🚀 Example

```python
from mapconfig import GeoMap

m = GeoMap()
m.add_marker("New Delhi", popup="Capital City")
m.add_circle("Hyderabad", radius=10000, color="green", popup="Cyber Hub")
m.add_custom_icon_marker("Chennai", icon_url="https://cdn-icons-png.flaticon.com/512/684/684908.png", popup="Beach City")

m.show()
