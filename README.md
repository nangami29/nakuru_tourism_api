# Nakuru County Spatial Tourism Dashboard

A production-grade geospatial analytics dashboard and REST API designed to map, 
filter, and analyze tourism attraction centers and hospitality infrastructure across Nakuru County, Kenya. 

Built as part of the **GitHub Finish-Up-A-Thon Challenge**, t
his project represents the complete evolution of a fragile, local prototype into a secure, cloud-native spatial application.

##  Live Demo & Deployment
* **Live Application:** (https://nakurutourismapi-huyz3rqncztd99gjwnqjea.streamlit.app/)
* **Database Host:** Neon PostgreSQL Cloud

---

## Architecture & Tech Stack

The application separates concerns between a robust spatial database, an enterprise backend framework,
and a highly responsive, data-driven user interface.

* **Backend Framework:** Django / GeoDjango (REST API ready)
* **Frontend Dashboard:** Streamlit
* **Geospatial Processing:** GDAL / GEOS / Proj (Ubuntu Linux layer)
* **Cloud Database:** Neon PostgreSQL (with PostGIS extensions)
* **Data Visualization:** Folium (Interactive Mapping) & Plotly Express (Statistical Analytics)

---

## The Completion Arc: Before vs. After

### The "Before" (The Abandoned Graveyard)
Initially developed as a local experiment in late 2025, 
the project sat stalled in a local repository due to standard production deployment friction. 
The local build relied on a localized Windows PostgreSQL instance and hardcoded environment structures. Migrating heavy C++ architectural dependencies like GDAL to a standardized server environment remained an unresolved bottleneck.

### The "After" (The Production Release)
Through the forcing function of the Finish-Up-A-Thon, the codebase was completely refactored for portability and cloud execution:
1. **System-Level Dependency Resolution:** Configured automated Ubuntu-level pathing via custom build configurations (`packages.txt`) to dynamically install the necessary C++ spatial libraries on server runtime.
2. **Cloud Database Migration:** Decoupled the state from local host infrastructure, migrating the entire dataset to a high-availability, remote Neon PostgreSQL cloud database instance.
3. **Enterprise Security Practices:** Eradicated hardcoded credentials, routing all database handshakes securely through environment runtime injection variables (`django-environ` and Streamlit Secrets management).

---

## Installation & Local Setup

To pull this repository and execute the spatial engine locally on your machine, follow the configuration steps below.

### 1. Clone the Repository
```bash
git clone (https://github.com/nangami29/nakuru_tourism_api.git)
cd nakuru_tourism_api
