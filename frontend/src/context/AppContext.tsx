import React, { createContext, useContext, useState, ReactNode } from 'react';
interface AppState {
  name: string;
  dateOfBirth: string;
  age: number;
  occupation: string;
  questions: any[];
  setName: (n: string) => void;
  setDateOfBirth: (d: string) => void;
  setAge: (a: number) => void;
  setOccupation: (o: string) => void;
  setQuestions: (q: any[]) => void;
}
const initialState: AppState = {
  name: '',
  dateOfBirth: '',
  age: 0,
  occupation: '',
  questions: [],
  setName: () => {},
  setDateOfBirth: () => {},
  setAge: () => {},
  setOccupation: () => {},
  setQuestions: () => {},
};
const AppContext = createContext<AppState>(initialState);
export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [name, setName] = useState('');
  const [dateOfBirth, setDateOfBirth] = useState('');
  const [age, setAge] = useState(0);
  const [occupation, setOccupation] = useState('');
  const [questions, setQuestions] = useState<any[]>([]);
  return (
    <AppContext.Provider
      value={{
        name, dateOfBirth, age, occupation, questions,
        setName, setDateOfBirth, setAge, setOccupation, setQuestions,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};
export const useAppContext = (): AppState => {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useAppContext must be used within AppProvider');
  return ctx;
};
export default AppContext;
