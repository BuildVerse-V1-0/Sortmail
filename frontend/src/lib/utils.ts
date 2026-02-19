import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function getSenderInfo(emailString: string | undefined): { name: string; email: string; initials: string } {
  if (!emailString) return { name: 'Unknown', email: '', initials: '??' };

  // Handle "Name <email@example.com>" format
  const match = emailString.match(/^(?:"?([^"]*)"?\s)?(?:<?(.+@[^>]+)>?)$/);
  if (match) {
    const name = match[1] || match[2].split('@')[0];
    const email = match[2];
    const initials = name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
    return { name, email, initials };
  }

  // Fallback for simple email
  return {
    name: emailString.split('@')[0],
    email: emailString,
    initials: emailString.substring(0, 2).toUpperCase()
  };
}
