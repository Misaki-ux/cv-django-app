import json
import math
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from bs4 import BeautifulSoup

from .models import SearchQuery, BusinessContact


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def search_google_maps(query, location, radius_km, api_key):
    results = []
    if not api_key:
        return results
    try:
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={api_key}"
        geo_resp = requests.get(geocode_url, timeout=10)
        geo_data = geo_resp.json()
        if geo_data.get("results"):
            loc = geo_data["results"][0]["geometry"]["location"]
            lat, lng = loc["lat"], loc["lng"]
        else:
            return results

        places_url = (
            f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            f"?location={lat},{lng}&radius={int(radius_km * 1000)}"
            f"&keyword={query}&type=restaurant|bar&key={api_key}"
        )
        resp = requests.get(places_url, timeout=15)
        data = resp.json()
        for place in data.get("results", [])[:20]:
            place_id = place.get("place_id", "")
            detail = {}
            if place_id:
                detail_url = (
                    f"https://maps.googleapis.com/maps/api/place/details/json"
                    f"?place_id={place_id}&fields=name,formatted_phone_number,"
                    f"website,formatted_address,rating,geometry&key={api_key}"
                )
                detail_resp = requests.get(detail_url, timeout=10)
                detail = detail_resp.json().get("result", {})

            results.append({
                "business_name": detail.get("name", place.get("name", "")),
                "address": detail.get("formatted_address", place.get("vicinity", "")),
                "phone": detail.get("formatted_phone_number", ""),
                "website": detail.get("website", ""),
                "rating": place.get("rating"),
                "latitude": place.get("geometry", {}).get("location", {}).get("lat"),
                "longitude": place.get("geometry", {}).get("location", {}).get("lng"),
                "source": "Google Maps",
            })
    except Exception as e:
        pass
    return results


def search_pages_jaunes(query, location):
    results = []
    try:
        url = f"https://www.pagesjaunes.fr/annuaire/chercherlespro?quoiqui={query}&ou={location}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            listings = soup.select(".bi-header-title, .bi-denomination")
            for listing in listings[:15]:
                name = listing.get_text(strip=True)
                parent = listing.find_parent("div", class_="bi")
                phone = ""
                address = ""
                website = ""
                if parent:
                    phone_el = parent.select_one(".bi-phone, .tel")
                    if phone_el:
                        phone = phone_el.get_text(strip=True)
                    addr_el = parent.select_one(".bi-address, .adresse")
                    if addr_el:
                        address = addr_el.get_text(strip=True)
                    web_el = parent.select_one("a[href*='http']")
                    if web_el:
                        website = web_el.get("href", "")
                if name:
                    results.append({
                        "business_name": name,
                        "address": address,
                        "phone": phone,
                        "website": website,
                        "source": "Pages Jaunes",
                    })
    except Exception:
        pass
    return results


def search_linkedin(query, location):
    results = []
    try:
        search_url = (
            f"https://www.google.com/search?q=site:linkedin.com/company+"
            f"{query}+{location}+restaurant+bar+HR+contact"
        )
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        resp = requests.get(search_url, headers=headers, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            for link in soup.select("a[href*='linkedin.com/company']")[:10]:
                href = link.get("href", "")
                title = link.get_text(strip=True)
                if "linkedin.com/company" in href and title:
                    results.append({
                        "business_name": title,
                        "linkedin_url": href.split("&")[0].replace("/url?q=", ""),
                        "source": "LinkedIn",
                    })
    except Exception:
        pass
    return results


@login_required
def job_search(request):
    results = []
    search_query = None

    if request.method == "POST":
        query = request.POST.get("query", "restaurant bar")
        location = request.POST.get("location", "")
        radius = float(request.POST.get("radius", 10))
        source = request.POST.get("source", "google_maps")

        search_query = SearchQuery.objects.create(
            user=request.user,
            query=query,
            location=location,
            radius_km=radius,
            source=source,
        )

        if source == "google_maps":
            results = search_google_maps(query, location, radius, settings.GOOGLE_MAPS_API_KEY)
        elif source == "pages_jaunes":
            results = search_pages_jaunes(query, location)
        elif source == "linkedin":
            results = search_linkedin(query, location)

        for r in results:
            BusinessContact.objects.create(
                search_query=search_query,
                user=request.user,
                business_name=r.get("business_name", ""),
                address=r.get("address", ""),
                phone=r.get("phone", ""),
                email=r.get("email", ""),
                website=r.get("website", ""),
                linkedin_url=r.get("linkedin_url", ""),
                source=r.get("source", ""),
                latitude=r.get("latitude"),
                longitude=r.get("longitude"),
                rating=r.get("rating"),
            )

        search_query.results_count = len(results)
        search_query.save()

        if results:
            messages.success(request, _("Found {} results!").format(len(results)))
        else:
            messages.warning(request, _("No results found. Try a different search or source."))

    recent_searches = SearchQuery.objects.filter(user=request.user)[:10]
    return render(request, "job_search/search.html", {
        "results": results,
        "search_query": search_query,
        "recent_searches": recent_searches,
    })


@login_required
def search_results(request, pk):
    search = get_object_or_404(SearchQuery, pk=pk, user=request.user)
    contacts = search.contacts.all()
    return render(request, "job_search/results.html", {
        "search": search,
        "contacts": contacts,
    })


@login_required
def saved_contacts(request):
    contacts = BusinessContact.objects.filter(user=request.user, is_saved=True)
    return render(request, "job_search/saved.html", {"contacts": contacts})


@login_required
def toggle_save_contact(request, pk):
    contact = get_object_or_404(BusinessContact, pk=pk, user=request.user)
    contact.is_saved = not contact.is_saved
    contact.save()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"saved": contact.is_saved})
    return redirect(request.META.get("HTTP_REFERER", "job_search"))


@login_required
def contact_detail(request, pk):
    contact = get_object_or_404(BusinessContact, pk=pk, user=request.user)
    if request.method == "POST":
        contact.notes = request.POST.get("notes", "")
        contact.save()
        messages.success(request, _("Notes updated!"))
    return render(request, "job_search/contact_detail.html", {"contact": contact})
