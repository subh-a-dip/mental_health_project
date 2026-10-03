export function calculateAge(dateOfBirth: string): number {
  if (!dateOfBirth) return 0;
  const today = new Date();
  const birth = new Date(dateOfBirth);
  let age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--;
  }
  return age;
}
export function formatDate(date: Date): string {
  return date.toISOString().split('T')[0];
}
export function getRatingDescription(value: number): string {
  if (value <= 2) return 'Very Low';
  if (value <= 4) return 'Low';
  if (value <= 6) return 'Moderate';
  if (value <= 8) return 'High';
  return 'Very High';
}
