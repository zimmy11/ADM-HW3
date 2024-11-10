import os
import shutil

# i am dumb so i have to do this separately
MAIN_FOLDER = "michelin_restaurants"

def organize_folders():
    """
    Moves all folders with the prefix 'page_' into the MAIN_FOLDER.
    """
    if not os.path.exists(MAIN_FOLDER):
        os.makedirs(MAIN_FOLDER) #create main folder
        print(f"Created main folder: {MAIN_FOLDER}")

    for folder_name in os.listdir(): #loop through directory
        if os.path.isdir(folder_name) and folder_name.startswith("page_"): # we need the folder that starts with page_
            target_path = os.path.join(MAIN_FOLDER, folder_name)
            
            shutil.move(folder_name, target_path) # move folders to main folder
            #print(f"Moved folder '{folder_name}' to '{MAIN_FOLDER}'")

    print("All page_* folders have been organized into the main folder.")

#if __name__ == "__main__":
    #organize_folders()
