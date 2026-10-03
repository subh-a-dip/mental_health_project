import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import ScoreCard from '@/components/ScoreCard';
import RecommendationCard from '@/components/RecommendationCard';
import Disclaimer from '@/components/Disclaimer';
import type { AssessmentResponse, WellResultData } from '@/types/assessment';
import { formatDate } from '@/utils/ageCalculator';
import { jsPDF } from 'jspdf';
import 'jspdf-autotable';

const WellbeingResult: React.FC = () => {
  const location = useLocation();
  const state = location.state as { result: AssessmentResponse; userProfile: { name: string; dateOfBirth: string; age: number; occupation: string } } | null;
  const [showDisclaimer, setShowDisclaimer] = useState(false);

  if (!state) {
    return (
      <div className="text-center py-16">
        <p className="text-slate-500">No assessment data found.</p>
      </div>
    );
  }

  const { result, userProfile } = state;
  const assessmentDate = formatDate(new Date());

  const wellResultData: WellResultData = {
    ...result,
    userProfile,
    assessmentDate,
  };

  const getCategoryEmoji = (cat: string) => {
    if (cat.includes('Excellent')) return '🌟';
    if (cat.includes('Good')) return '😊';
    if (cat.includes('Moderate')) return '😐';
    return '⚠️';
  };

  const downloadPDF = () => {
    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    let y = 20;

    // Title
    doc.setFontSize(24);
    doc.setTextColor(30, 41, 59);
    doc.text('MindWell AI - Wellbeing Assessment Report', pageWidth / 2, y, { align: 'center' });
    y += 10;

    // Subtitle
    doc.setFontSize(12);
    doc.setTextColor(100, 116, 139);
    doc.text(`Generated on ${assessmentDate}`, pageWidth / 2, y, { align: 'center' });
    y += 15;

    // User Profile
    doc.setFontSize(14);
    doc.setTextColor(30, 41, 59);
    doc.text('Personal Information', 14, y);
    y += 8;

    doc.setFontSize(11);
    doc.setTextColor(71, 85, 105);
    const profileData = [
      ['Name', userProfile.name],
      ['Age', String(userProfile.age)],
      ['Occupation', userProfile.occupation],
      ['Date of Birth', userProfile.dateOfBirth],
      ['Assessment Date', assessmentDate],
    ];
    (doc as any).autoTable({
      startY: y,
      head: [['Field', 'Value']],
      body: profileData,
      theme: 'grid',
      headStyles: { fillColor: [59, 130, 246], textColor: 255 },
      styles: { fontSize: 10, cellPadding: 3 },
      margin: { left: 14, right: 14 },
    });
    y = (doc as any).lastAutoTable.finalY + 10;

    // Score Summary
    doc.setFontSize(14);
    doc.setTextColor(30, 41, 59);
    doc.text('Wellness Score Summary', 14, y);
    y += 8;

    const categoryColor = result.category.includes('Excellent') || result.category.includes('Good') 
      ? [58, 157, 99] 
      : result.category.includes('Moderate') 
        ? [245, 158, 11] 
        : [220, 38, 38];

    doc.setFontSize(28);
    doc.setTextColor(categoryColor[0], categoryColor[1], categoryColor[2]);
    doc.text(`${result.score}/100`, pageWidth / 2, y, { align: 'center' });
    y += 10;

    doc.setFontSize(14);
    doc.setTextColor(30, 41, 59);
    doc.text(result.category, pageWidth / 2, y, { align: 'center' });
    y += 10;

    // Category breakdown
    if (result.category_breakdown) {
      const breakdownData = Object.entries(result.category_breakdown).map(([cat, val]) => [
        cat.charAt(0).toUpperCase() + cat.slice(1).replace('_', ' '),
        `${val}/10`
      ]);
      (doc as any).autoTable({
        startY: y,
        head: [['Category', 'Score']],
        body: breakdownData,
        theme: 'grid',
        headStyles: { fillColor: [59, 130, 246], textColor: 255 },
        styles: { fontSize: 10, cellPadding: 3 },
        margin: { left: 14, right: 14 },
      });
      y = (doc as any).lastAutoTable.finalY + 10;
    }

    // Strengths
    if (result.strengths.length > 0) {
      doc.setFontSize(14);
      doc.setTextColor(30, 41, 59);
      doc.text('Key Strengths', 14, y);
      y += 8;
      const strengthsData = result.strengths.map((s, i) => [String(i + 1), s]);
      (doc as any).autoTable({
        startY: y,
        head: [['#', 'Strength']],
        body: strengthsData,
        theme: 'grid',
        headStyles: { fillColor: [58, 157, 99], textColor: 255 },
        styles: { fontSize: 10, cellPadding: 3 },
        margin: { left: 14, right: 14 },
      });
      y = (doc as any).lastAutoTable.finalY + 10;
    }

    // Areas to Improve
    if (result.areas_to_improve.length > 0) {
      doc.setFontSize(14);
      doc.setTextColor(30, 41, 59);
      doc.text('Recommended Areas to Improve', 14, y);
      y += 8;
      const areasData = result.areas_to_improve.map((area, i) => [
        String(i + 1),
        area.category,
        area.current,
        area.recommendation,
        area.action
      ]);
      (doc as any).autoTable({
        startY: y,
        head: [['#', 'Category', 'Current', 'Recommendation', 'Action']],
        body: areasData,
        theme: 'grid',
        headStyles: { fillColor: [245, 158, 11], textColor: 255 },
        styles: { fontSize: 9, cellPadding: 3, overflow: 'linebreak' },
        columnStyles: { 3: { cellWidth: 50 }, 4: { cellWidth: 50 } },
        margin: { left: 14, right: 14 },
      });
      y = (doc as any).lastAutoTable.finalY + 10;
    }

    // Notes
    if (result.notes.length > 0) {
      doc.setFontSize(14);
      doc.setTextColor(30, 41, 59);
      doc.text('Wellness Notes', 14, y);
      y += 8;
      const notesData = result.notes.map((note, i) => [String(i + 1), note]);
      (doc as any).autoTable({
        startY: y,
        head: [['#', 'Note']],
        body: notesData,
        theme: 'grid',
        headStyles: { fillColor: [59, 130, 246], textColor: 255 },
        styles: { fontSize: 10, cellPadding: 3, overflow: 'linebreak' },
        margin: { left: 14, right: 14 },
      });
      y = (doc as any).lastAutoTable.finalY + 10;
    }

    // Disclaimer
    doc.setFontSize(10);
    doc.setTextColor(148, 163, 184);
    doc.text('Disclaimer: This assessment is a general indicator and not a clinical diagnosis.', 14, y);
    y += 5;
    doc.text('Please consult a mental health professional for personalized guidance.', 14, y);
    y += 5;
    doc.text(`Report generated by MindWell AI on ${assessmentDate}`, 14, y);

    // Save
    doc.save(`MindWell_Report_${userProfile.name.replace(/\s+/g, '_')}_${assessmentDate}.pdf`);
  };

  return (
    <div className="animate-fade-in max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 text-center mb-2">Your Wellbeing Insights</h1>
      <p className="text-center text-slate-500 mb-8">{assessmentDate}</p>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <ScoreCard result={wellResultData} />
        <div className="space-y-4">
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-800 mb-3">Summary</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-slate-500">Name</span><span className="font-medium">{userProfile.name}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Age</span><span className="font-medium">{userProfile.age}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Occupation</span><span className="font-medium">{userProfile.occupation}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Date</span><span className="font-medium">{assessmentDate}</span></div>
            </div>
          </div>
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-800 mb-3">Key Strengths</h3>
            <ul className="space-y-2">
              {result.strengths.map((s, i) => (
                <li key={i} className="flex items-center gap-2 text-sm text-slate-600">
                  <span className="text-sage-600 flex-shrink-0">✓</span> {s}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
      <div className="mb-8">
        <h2 className="text-xl font-bold text-slate-900 mb-4">
          {getCategoryEmoji(result.category)} {result.category}
        </h2>
        {result.areas_to_improve.length > 0 && (
          <h3 className="text-lg font-semibold text-slate-800 mb-4">Recommended Areas to Improve</h3>
        )}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {result.areas_to_improve.map((area, i) => (
            <RecommendationCard key={i} area={area} />
          ))}
        </div>
      </div>
      {result.notes.length > 0 && (
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm mb-8">
          <h3 className="text-lg font-semibold text-slate-800 mb-4">Your Wellness Notes</h3>
          <ul className="space-y-2">
            {result.notes.map((note, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-600">
                <span className="text-primary-500 flex-shrink-0 mt-0.5">•</span> {note}
              </li>
            ))}
          </ul>
        </div>
      )}
      <Disclaimer />
      <div className="flex flex-col sm:flex-row gap-4 mt-8">
        <button
          onClick={() => setShowDisclaimer(!showDisclaimer)}
          className="px-6 py-3 border border-slate-300 text-slate-700 font-semibold rounded-xl hover:bg-slate-50 transition-colors"
        >
          {showDisclaimer ? 'Hide' : 'Show'} Details
        </button>
        <button
          onClick={downloadPDF}
          className="px-8 py-3 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 transition-colors flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
          Download PDF Report
        </button>
      </div>
      {showDisclaimer && (
        <div className="mt-6 bg-slate-50 rounded-xl p-4 text-sm text-slate-600 animate-fade-in">
          <p className="font-semibold text-slate-800 mb-2">Assessment Details</p>
          <p>This assessment uses AI-powered analysis of your responses to provide general wellbeing insights. The score and categories are based on statistical patterns and should not be used as a substitute for professional medical advice, diagnosis, or treatment.</p>
          <p className="mt-2">If you are experiencing a mental health crisis, please contact emergency services or a crisis helpline immediately.</p>
        </div>
      )}
    </div>
  );
};

export default WellbeingResult;