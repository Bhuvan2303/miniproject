import json
contacts = []

try:
    with open("contacts.json", "r") as f:
        contacts = json.load(f)
except FileNotFoundError:
    contacts = []

def add_contact():
    name = input("Enter name: ")
    phone = input("Enter phone number: ")
    contact = {
        "name": name,
        "phone": phone
    }
    contacts.append(contact)
    print("Contact added!")

def view_contacts():
    for c in contacts:
        print("Name:", c["name"], "- Phone:", c["phone"])

def save_contacts():
    with open("contacts.json", "w") as f:
        json.dump(contacts, f, indent=4)

while True:
    print("\n1. Add Contact")
    print("2. View Contact")
    print("3. Save")
    print("4. Exit")

    choice = int(input("Choose option: "))

    if choice == 1:
        add_contact()
    elif choice == 2:
        view_contacts()
    elif choice == 3:
        save_contacts()
        print("Saved!")
    elif choice == 4:
        save_contacts()
        print("Exiting...")
        break
    else:
        print("Invalid choice!")