import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { AppProvider } from '@/context/AppContext';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import Home from '@/pages/Home';
import About from '@/pages/About';
import Privacy from '@/pages/Privacy';
import DisclaimerPage from '@/pages/Disclaimer';
import WellbeingIntro from '@/pages/WellbeingIntro';
import UserInformation from '@/pages/UserInformation';
import Assessment from '@/pages/Assessment';
import AssessmentProcessing from '@/pages/AssessmentProcessing';
import WellbeingResult from '@/pages/WellbeingResult';
import SentimentAnalysis from '@/pages/SentimentAnalysis';

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1">{children}</main>
      <Footer />
    </div>
  );
};

const App: React.FC = () => {
  return (
    <AppProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/privacy" element={<Privacy />} />
          <Route path="/disclaimer" element={<DisclaimerPage />} />
          <Route path="/wellbeing-intro" element={<WellbeingIntro />} />
          <Route path="/user-info" element={<UserInformation />} />
          <Route path="/assessment" element={<Assessment />} />
          <Route path="/assessment-processing" element={<AssessmentProcessing />} />
          <Route path="/wellbeing-result" element={<WellbeingResult />} />
          <Route path="/sentiment" element={<SentimentAnalysis />} />
        </Routes>
      </Layout>
    </AppProvider>
  );
};

export default App;
