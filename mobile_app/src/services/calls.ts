import { Linking } from "react-native";

export async function startPhoneCall(number: string) {
  const url = `tel:${number}`;
  const supported = await Linking.canOpenURL(url);
  if (!supported) {
    throw new Error("Phone calls are not supported on this device");
  }
  await Linking.openURL(url);
}
