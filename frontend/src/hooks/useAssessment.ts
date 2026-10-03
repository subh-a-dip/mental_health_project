import type { Question, AssessmentPayload, AssessmentResponse } from '@/types/assessment';
export interface UseAssessmentReturn {
  questions: Question[];
  responses: Record<string, number>;
  currentPage: number;
  setResponse: (id: string, value: number) => void;
  goNext: () => void;
  goPrev: () => void;
  submitAssessment: (payload: AssessmentPayload) => Promise<AssessmentResponse>;
  isLoading: boolean;
  error: string | null;
  totalPages: number;
  allAnswered: boolean;
}
export type AssessmentStatus = 'idle' | 'loading' | 'error' | 'success';
