import type { Question, AssessmentPayload, AssessmentResponse } from '@/types/assessment';
import { API_BASE } from './config';
export async function predictMentalHealth(payload: AssessmentPayload): Promise<AssessmentResponse> {
  const response = await fetch(`${API_BASE}/mental-health/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`Prediction failed: ${response.status}`);
  }
  return response.json() as Promise<AssessmentResponse>;
}
export async function getQuestions(occupation?: string): Promise<Question[]> {
  const url = occupation
    ? `${API_BASE}/mental-health/questions?occupation=${encodeURIComponent(occupation)}`
    : `${API_BASE}/mental-health/questions`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch questions: ${response.status}`);
  }
  return response.json() as Promise<Question[]>;
}
