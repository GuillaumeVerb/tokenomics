import html2pdf from 'html2pdf.js'

interface ExportToPDFOptions {
  filename?: string
  margin?: number
  pageSize?: string
}

interface Html2PdfOptions {
  margin?: number
  filename?: string
  image?: {
    type?: string
    quality?: number
  }
  html2canvas?: {
    scale?: number
    [key: string]: any
  }
  jsPDF?: {
    unit?: string
    format?: string
    orientation?: 'portrait' | 'landscape'
    [key: string]: any
  }
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