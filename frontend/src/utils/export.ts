import html2pdf from 'html2pdf.js'
import type { Html2PdfOptions } from '../types/html2pdf'

interface ExportToPDFOptions {
  filename?: string
  margin?: number
  pageSize?: string
}

export const exportToPDF = async (
  element: HTMLElement,
  options: ExportToPDFOptions = {}
) => {
  const {
    filename = 'tokenomics-simulation.pdf',
    margin = 10,
    pageSize = 'a4',
  } = options

  const opt: Html2PdfOptions = {
    margin,
    filename,
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2 },
    jsPDF: { unit: 'mm', format: pageSize, orientation: 'landscape' as const },
  }

  try {
    await html2pdf().set(opt).from(element).save()
    return true
  } catch (error) {
    console.error('Error exporting to PDF:', error)
    return false
  }
} 