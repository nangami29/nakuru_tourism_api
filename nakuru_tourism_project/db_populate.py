import os
import django
import pandas as pd 

# 1. Identify the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nakuru_tourism_project.settings')

# 2. Set the missing environment variable FIRST
os.environ['SECRET_KEY'] = 'local-migration-bypassed-key-123'

# 3. Boot the Django engine 
django.setup()

from tour_app.models import AttractionSite, Pricing , Hotel, VisitorStat, Category

print("Handshake successful! Django connected to PostgreSQL without errors.") 

def populate_database():
    # 1. Categories
    file_path = 'tour_app/exports/categories.csv'
    if os.path.exists(file_path):
        print("Loading Categories...")
        df = pd.read_csv(file_path)

    
        for i, row in df.iterrows():
            row_dict = row.dropna().to_dict()
            
            row_dict.pop('id', None)
            
            Category.objects.update_or_create(
                name=row_dict.get('name'), 
                defaults=row_dict
            )
        print("Categories synced.")
    else:
        print ("Missing: categories.csv")
    # 2. Attractions
    file_attraction = "tour_app/exports/clean_attractions.csv"
    if os.path.exists(file_attraction):
        print("Loading Attractions...")
        df = pd.read_csv(file_attraction)
        for i, row in df.iterrows():
            row_dict = row.dropna().to_dict()
            
            row_dict.pop('id', None)
            
            category_name = row_dict.pop('category', None) 
            if category_name:
                category_obj = Category.objects.filter(name=category_name).first()
                row_dict['category'] = category_obj 
                
            AttractionSite.objects.update_or_create(
                name=row_dict.get('name'), 
                defaults=row_dict
            )
        print("Attractions synced.")
    else:
        print("Missing: clean_attractions.csv")
    
    # 3. Pricing
    prices_file = "tour_app/exports/prices1.csv"
    if os.path.exists(prices_file):
        print("Loading Pricing...")
        
        Pricing.objects.all().delete()
        
        df = pd.read_csv(prices_file)
        
        # Patch blank prices to 0.00
        df['price'] = df['price'].fillna(0.00) 
        
        for i, row in df.iterrows():
            row_dict = row.dropna().to_dict()
            
            attraction_name = row_dict.pop('attraction_site', None)
            if attraction_name:
                attraction_obj = AttractionSite.objects.filter(name=attraction_name).first()
                row_dict['attraction_site'] = attraction_obj
            
            row_dict.pop('id', None)
            
            try:
                Pricing.objects.create(**row_dict)
            except Exception:
                pass
                
        print("Pricing synced.")
    else:
        print("Missing: prices1.csv")
    
    # 4. Hotels
    # 4. Hotels
    hotel_file = "tour_app/exports/hotels1.csv"
    if os.path.exists(hotel_file):
        print("Loading Hotels...")
        Hotel.objects.all().delete()
        
        df = pd.read_csv(hotel_file)
        
        for i, row in df.iterrows():
            row_dict = row.to_dict()
            
            # Safely convert all NaNs to true None values
            for k, v in row_dict.items():
                if pd.isna(v):
                    row_dict[k] = None
                    
            row_dict.pop('id', None)
            
            attraction_name = row_dict.pop('attraction_site', None)
            if attraction_name:
                attraction_obj = AttractionSite.objects.filter(name=attraction_name).first()
                row_dict['attraction_site'] = attraction_obj
                
            for text_field in ['address', 'contact_phone', 'contact_email', 'website', 'image']:
                if row_dict.get(text_field) is None:
                    row_dict[text_field] = ""
                    
             
            if row_dict.get('price_per_night') is None:
                row_dict['price_per_night'] = 0.00
                
            try:
                Hotel.objects.create(**row_dict)
            except Exception as e:
                print(f"FAILED to save {row_dict.get('name')}: {e}")
                
        print("Hotels synced.")
    else:
        print("Missing: hotels1.csv")
    # 5. Visitor Stats 
    file_stat = 'tour_app/exports/visitor_stats.csv' 
    if os.path.exists(file_stat):
        print("Loading Visitor Stats...")
        
        VisitorStat.objects.all().delete()
        
        df = pd.read_csv(file_stat)
        
        for i, row in df.iterrows():
            row_dict = row.dropna().to_dict()
            
            attraction_name = row_dict.pop('attraction_site', None)
            if attraction_name:
                attraction_obj = AttractionSite.objects.filter(name=attraction_name).first()
                row_dict['attraction_site'] = attraction_obj
                
            row_dict.pop('id', None)
            
            try:
                VisitorStat.objects.create(**row_dict)
            except Exception:
                pass
                
        print("Visitor Stats synced.")
    else:
        print(f"Missing: {file_stat}")
    print("All done! PostgreSQL is fully populated.")
if __name__ == '__main__':
    print("Starting data pipeline...")
    populate_database()