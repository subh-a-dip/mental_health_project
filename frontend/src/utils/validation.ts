export function validateNotEmpty(value: string): boolean {
  return value.trim().length > 0;
}
export function validateDate(dateStr: string): boolean {
  if (!dateStr) return false;
  const d = new Date(dateStr);
  return !isNaN(d.getTime());
}
export function validateAge(age: number): boolean {
  return age > 0 && age < 120;
}
export function validateTextLength(text: string, min: number = 1, max: number = 10000): boolean {
  return text.trim().length >= min && text.trim().length <= max;
}
export function validateQuestionsAnswered(responses: Record<string, number>, requiredIds: string[]): boolean {
  return requiredIds.every(id => responses[id] !== undefined && responses[id] !== null);
}
