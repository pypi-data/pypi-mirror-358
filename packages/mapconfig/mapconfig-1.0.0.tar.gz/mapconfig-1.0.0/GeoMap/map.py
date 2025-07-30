import folium
import requests
import webbrowser
import tempfile
import os

class GeoMap:
    def __init__(self):
        """Initialize without center. First place added will set center."""
        self._map = None
        self._has_center = False

    def _get_coordinates(self, place_name):
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": place_name, "format": "json", "limit": 1}
        response = requests.get(url, params=params, headers={"User-Agent": "simplegeomap-app"})
        if response.status_code == 200 and response.json():
            data = response.json()[0]
            return float(data['lat']), float(data['lon'])
        else:
            raise Exception(f"Place '{place_name}' not found.")

    def _init_map_if_needed(self, location):
        if not self._has_center:
            self._map = folium.Map(location=location, zoom_start=5)
            self._has_center = True

    def add_marker(self, place_name, popup=None):
        lat, lon = self._get_coordinates(place_name)
        self._init_map_if_needed([lat, lon])
        popup_text = popup if popup else place_name
        folium.Marker([lat, lon], popup=popup_text, tooltip=place_name).add_to(self._map)

    def add_circle(self, place_name, radius=500, color='blue', popup="Area"):
        lat, lon = self._get_coordinates(place_name)
        self._init_map_if_needed([lat, lon])
        folium.Circle([lat, lon], radius=radius, color=color, fill=True, popup=popup).add_to(self._map)

    def add_custom_icon_marker(self, place_name, icon_url, icon_size=(30, 30), popup="Custom Icon"):
        lat, lon = self._get_coordinates(place_name)
        self._init_map_if_needed([lat, lon])
        icon = folium.CustomIcon(icon_url, icon_size=icon_size)
        folium.Marker([lat, lon], icon=icon, popup=popup).add_to(self._map)

    def save(self, filepath="my_map.html"):
        if self._map:
            self._map.save(filepath)
        else:
            raise Exception("Map is empty. Add at least one place first.")

    def show(self):
        """Show map in browser directly without permanent file."""
        if self._map:
            tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
            self._map.save(tmp.name)
            webbrowser.open('file://' + os.path.realpath(tmp.name))
        else:
            raise Exception("Map is empty. Add at least one place first.")
