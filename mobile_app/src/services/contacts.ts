import * as Contacts from "expo-contacts";

export async function requestContactsAccess() {
  const { status } = await Contacts.requestPermissionsAsync();
  return status === "granted";
}

export async function searchContacts(query: string) {
  const access = await requestContactsAccess();
  if (!access) {
    return [];
  }

  const result = await Contacts.getContactsAsync({
    name: query,
    fields: [Contacts.Fields.PhoneNumbers]
  });

  return result.data.map((contact) => ({
    id: contact.id,
    name: contact.name,
    phone: contact.phoneNumbers?.[0]?.number ?? ""
  }));
}
