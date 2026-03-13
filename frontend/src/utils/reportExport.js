/**
 * Report Download Utilities
 * Export dashboard data to CSV, Excel, and PDF formats
 */

import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';
import jsPDF from 'jspdf';
import 'jspdf-autotable';

/**
 * Export uploaded files data to Excel
 */
export const exportFilesToExcel = (files, fileDetails = null) => {
  const wb = XLSX.utils.book_new();
  
  // Summary sheet
  const summaryData = (files || []).map(file => ({
    'File Name': file.filename || 'Unknown',
    'Rows': file.total_rows != null ? file.total_rows : 'N/A',
    'Columns': file.total_columns != null ? file.total_columns : 'N/A',
    'Type': file.source_type || file.status || 'N/A',
    'Uploaded': file.uploaded_at || 'N/A'
  }));
  
  if (summaryData.length === 0) {
    summaryData.push({ 'File Name': 'No files uploaded', 'Rows': '', 'Columns': '', 'Type': '', 'Uploaded': '' });
  }
  
  const summaryWs = XLSX.utils.json_to_sheet(summaryData);
  XLSX.utils.book_append_sheet(wb, summaryWs, 'Files Summary');
  
  // If file details are provided, add detailed analytics
  if (fileDetails) {
    const analyticsData = [
      ['Metric', 'Value'],
      ['Total Rows', fileDetails.analytics.total_rows],
      ['Total Columns', fileDetails.analytics.total_columns],
      ['File Name', fileDetails.filename]
    ];
    
    const analyticsWs = XLSX.utils.aoa_to_sheet(analyticsData);
    XLSX.utils.book_append_sheet(wb, analyticsWs, 'Analytics');
    
    // Add column information
    if (fileDetails.analytics.columns) {
      const columnsData = fileDetails.analytics.columns.map((col, idx) => ({
        'Column': col,
        'Data Type': fileDetails.analytics.data_types[col] || 'Unknown',
        'Missing Values': fileDetails.analytics.missing_values[col] || 0
      }));
      
      const columnsWs = XLSX.utils.json_to_sheet(columnsData);
      XLSX.utils.book_append_sheet(wb, columnsWs, 'Columns Info');
    }
    
    // Add sample data
    if (fileDetails.sample_data && fileDetails.sample_data.length > 0) {
      const sampleWs = XLSX.utils.json_to_sheet(fileDetails.sample_data);
      XLSX.utils.book_append_sheet(wb, sampleWs, 'Sample Data');
    }
  }
  
  // Generate file
  const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
  const data = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
  const fileName = `Analiyx_Report_${new Date().toISOString().split('T')[0]}.xlsx`;
  saveAs(data, fileName);
};

/**
 * Export data to CSV
 */
export const exportToCSV = (data, filename) => {
  const ws = XLSX.utils.json_to_sheet(data);
  const csv = XLSX.utils.sheet_to_csv(ws);
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  saveAs(blob, `${filename}_${new Date().toISOString().split('T')[0]}.csv`);
};

/**
 * Export dashboard analytics to PDF
 */
export const exportDashboardToPDF = (dashboardData) => {
  const doc = new jsPDF();
  
  // Title
  doc.setFontSize(20);
  doc.text('Analiyx Dashboard Report', 14, 22);
  
  // Date
  doc.setFontSize(10);
  doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 30);
  
  let yPos = 40;
  
  // User Info
  if (dashboardData.user) {
    doc.setFontSize(14);
    doc.text('Account Information', 14, yPos);
    yPos += 10;
    
    doc.setFontSize(10);
    doc.text(`Name: ${dashboardData.user.name}`, 14, yPos);
    yPos += 6;
    doc.text(`Email: ${dashboardData.user.email}`, 14, yPos);
    yPos += 6;
    doc.text(`Plan: ${dashboardData.user.plan}`, 14, yPos);
    yPos += 6;
    doc.text(`Credits: ${dashboardData.user.credits}`, 14, yPos);
    yPos += 15;
  }
  
  // Uploaded Files
  if (dashboardData.files && dashboardData.files.length > 0) {
    doc.setFontSize(14);
    doc.text('Uploaded Files', 14, yPos);
    yPos += 10;
    
    const fileTableData = dashboardData.files.map(file => [
      file.filename,
      file.total_rows.toString(),
      file.total_columns.toString(),
      file.status
    ]);
    
    doc.autoTable({
      startY: yPos,
      head: [['File Name', 'Rows', 'Columns', 'Status']],
      body: fileTableData,
      theme: 'grid',
      headStyles: { fillColor: [139, 92, 246] }
    });
    
    yPos = doc.lastAutoTable.finalY + 15;
  }
  
  // Connected Data Sources
  if (dashboardData.connectedSources && dashboardData.connectedSources.length > 0) {
    // Add new page if needed
    if (yPos > 250) {
      doc.addPage();
      yPos = 20;
    }
    
    doc.setFontSize(14);
    doc.text('Connected Data Sources', 14, yPos);
    yPos += 10;
    
    dashboardData.connectedSources.forEach(source => {
      doc.setFontSize(12);
      doc.text(source.name, 14, yPos);
      yPos += 6;
      
      doc.setFontSize(9);
      const metrics = Object.entries(source.metrics)
        .map(([key, value]) => `${key}: ${value}`)
        .join(', ');
      
      const splitMetrics = doc.splitTextToSize(metrics, 180);
      doc.text(splitMetrics, 14, yPos);
      yPos += splitMetrics.length * 5 + 8;
      
      if (yPos > 270) {
        doc.addPage();
        yPos = 20;
      }
    });
  }
  
  // Save PDF
  doc.save(`Analiyx_Dashboard_Report_${new Date().toISOString().split('T')[0]}.pdf`);
};

/**
 * Export AI Visibility insights to PDF
 */
export const exportAIVisibilityToPDF = (insights) => {
  const doc = new jsPDF();
  
  doc.setFontSize(20);
  doc.text('AI Visibility Report', 14, 22);
  
  doc.setFontSize(10);
  doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 30);
  
  let yPos = 45;
  
  // Platform insights table
  const tableData = insights.map(insight => [
    insight.platform,
    insight.appearances.toString(),
    insight.ranking,
    insight.trend.toUpperCase()
  ]);
  
  doc.autoTable({
    startY: yPos,
    head: [['Platform', 'Appearances', 'Ranking', 'Trend']],
    body: tableData,
    theme: 'grid',
    headStyles: { fillColor: [139, 92, 246] }
  });
  
  doc.save(`AI_Visibility_Report_${new Date().toISOString().split('T')[0]}.pdf`);
};

/**
 * Download comprehensive dashboard report
 */
export const downloadComprehensiveReport = async (dashboardData, format = 'excel') => {
  if (format === 'excel') {
    exportFilesToExcel(dashboardData.files || [], dashboardData.fileDetails);
  } else if (format === 'pdf') {
    exportDashboardToPDF(dashboardData);
  } else if (format === 'csv') {
    exportToCSV(dashboardData.files || [], 'Analiyx_Files');
  }
};
