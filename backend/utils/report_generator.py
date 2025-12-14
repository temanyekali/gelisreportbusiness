"""
Report Generation Utilities for PDF and Excel Export
Professional format with company branding
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO
from datetime import datetime
import xlsxwriter
from typing import Dict, List, Any
import os

class ReportGenerator:
    """Professional report generator for GELIS system"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#3b82f6'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        # Header info style
        self.styles.add(ParagraphStyle(
            name='HeaderInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#6b7280'),
            spaceAfter=6
        ))
    
    def _add_header(self, elements: List, title: str, report_date: datetime):
        """Add professional header to report"""
        # Company name
        company_name = Paragraph(
            "<b>GELIS</b><br/>Gerbang Elektronik Layanan Informasi Sistem",
            self.styles['CustomTitle']
        )
        elements.append(company_name)
        elements.append(Spacer(1, 0.2 * inch))
        
        # Report title
        report_title = Paragraph(title, self.styles['CustomSubtitle'])
        elements.append(report_title)
        
        # Report date
        date_str = report_date.strftime("%d %B %Y, %H:%M WIB")
        report_date_p = Paragraph(
            f"<i>Tanggal Laporan: {date_str}</i>",
            self.styles['HeaderInfo']
        )
        elements.append(report_date_p)
        elements.append(Spacer(1, 0.3 * inch))
    
    def _add_footer(self, canvas, doc):
        """Add footer to each page"""
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)
        
        # Page number
        page_num = canvas.getPageNumber()
        text = f"Halaman {page_num}"
        canvas.drawRightString(7.5 * inch, 0.5 * inch, text)
        
        # Generated timestamp
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        canvas.drawString(1 * inch, 0.5 * inch, f"Generated: {timestamp}")
        
        canvas.restoreState()
    
    def generate_executive_summary_pdf(self, data: Dict[str, Any]) -> BytesIO:
        """Generate Executive Summary Report in PDF format"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.75*inch)
        elements = []
        
        # Header
        self._add_header(
            elements,
            "LAPORAN RINGKASAN EKSEKUTIF",
            data.get('report_generated_at', datetime.now())
        )
        
        # Period info
        period_text = f"Periode: {data.get('period_start', '').strftime('%d/%m/%Y')} - {data.get('period_end', '').strftime('%d/%m/%Y')}"
        elements.append(Paragraph(period_text, self.styles['Normal']))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Overall Summary Table
        summary_data = [
            ['RINGKASAN KEUANGAN', ''],
            ['Total Pendapatan', f"Rp {data.get('total_revenue', 0):,.0f}"],
            ['Total Pengeluaran', f"Rp {data.get('total_expenses', 0):,.0f}"],
            ['Laba Bersih', f"Rp {data.get('net_profit', 0):,.0f}"],
            ['Margin Keuntungan', f"{data.get('overall_profit_margin', 0):.2f}%"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')]),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Business Units Performance
        if data.get('business_units'):
            elements.append(Paragraph("KINERJA PER UNIT BISNIS", self.styles['CustomSubtitle']))
            elements.append(Spacer(1, 0.1 * inch))
            
            bu_data = [['Unit Bisnis', 'Pendapatan', 'Pengeluaran', 'Laba', 'Margin', 'Orders']]
            for bu in data['business_units']:
                bu_data.append([
                    bu['business_name'],
                    f"Rp {bu['total_revenue']:,.0f}",
                    f"Rp {bu['total_expenses']:,.0f}",
                    f"Rp {bu['net_profit']:,.0f}",
                    f"{bu['profit_margin']:.1f}%",
                    f"{bu['completed_orders']}/{bu['total_orders']}"
                ])
            
            bu_table = Table(bu_data, colWidths=[1.5*inch, 1.3*inch, 1.3*inch, 1.3*inch, 0.8*inch, 0.8*inch])
            bu_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ]))
            elements.append(bu_table)
            elements.append(Spacer(1, 0.3 * inch))
        
        # Top Performers
        elements.append(Paragraph("TOP PERFORMERS", self.styles['CustomSubtitle']))
        performers_data = [
            ['Best Performing Business', data.get('best_performing_business', 'N/A')],
            ['Highest Revenue Business', data.get('highest_revenue_business', 'N/A')],
            ['Highest Margin Business', data.get('highest_margin_business', 'N/A')],
        ]
        
        performers_table = Table(performers_data, colWidths=[2.5*inch, 3*inch])
        performers_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecfdf5')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#10b981')),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(performers_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Alerts
        if data.get('alerts'):
            elements.append(Paragraph("PERINGATAN & PERHATIAN", self.styles['CustomSubtitle']))
            for alert in data['alerts'][:5]:  # Max 5 alerts
                alert_p = Paragraph(f"⚠️ {alert}", self.styles['Normal'])
                elements.append(alert_p)
                elements.append(Spacer(1, 0.1 * inch))
        
        # Recommendations
        if data.get('recommendations'):
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(Paragraph("REKOMENDASI", self.styles['CustomSubtitle']))
            for rec in data['recommendations'][:5]:  # Max 5 recommendations
                rec_p = Paragraph(f"💡 {rec}", self.styles['Normal'])
                elements.append(rec_p)
                elements.append(Spacer(1, 0.1 * inch))
        
        # Build PDF
        doc.build(elements, onFirstPage=self._add_footer, onLaterPages=self._add_footer)
        buffer.seek(0)
        return buffer
    
    def generate_ppob_shift_pdf(self, data: Dict[str, Any]) -> BytesIO:
        """Generate PPOB Shift Report in PDF format"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.75*inch)
        elements = []
        
        # Header
        self._add_header(
            elements,
            "LAPORAN SHIFT PPOB",
            data.get('created_at', datetime.now())
        )
        
        # Shift Info
        shift_info = [
            ['Tanggal', data.get('report_date', datetime.now()).strftime('%d %B %Y')],
            ['Shift', f"Shift {data.get('shift', 1)}"],
            ['Petugas', data.get('petugas_name', '-')],
            ['Total Transaksi', str(data.get('total_transactions', 0))],
        ]
        
        info_table = Table(shift_info, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f3f4f6')),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Product Breakdown
        elements.append(Paragraph("BREAKDOWN PRODUK", self.styles['CustomSubtitle']))
        
        breakdown_data = [['Jenis Produk', 'Jumlah Trx', 'Total Amount', 'Fee', 'Komisi']]
        for product in data.get('product_breakdown', []):
            breakdown_data.append([
                product['product_type'],
                str(product['transaction_count']),
                f"Rp {product['total_amount']:,.0f}",
                f"Rp {product['total_fee']:,.0f}",
                f"Rp {product['total_commission']:,.0f}",
            ])
        
        # Add totals row
        breakdown_data.append([
            'TOTAL',
            str(data.get('total_transactions', 0)),
            f"Rp {data.get('total_amount', 0):,.0f}",
            f"Rp {data.get('total_fee', 0):,.0f}",
            f"Rp {data.get('total_commission', 0):,.0f}",
        ])
        
        breakdown_table = Table(breakdown_data, colWidths=[1.8*inch, 1*inch, 1.5*inch, 1.2*inch, 1.2*inch])
        breakdown_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f9fafb')]),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#dbeafe')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        elements.append(breakdown_table)
        
        # Build PDF
        doc.build(elements, onFirstPage=self._add_footer, onLaterPages=self._add_footer)
        buffer.seek(0)
        return buffer
    
    def generate_executive_summary_excel(self, data: Dict[str, Any]) -> BytesIO:
        """Generate Executive Summary Report in Excel format"""
        buffer = BytesIO()
        workbook = xlsxwriter.Workbook(buffer, {'in_memory': True})
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'bg_color': '#1e40af',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter'
        })
        
        subheader_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#3b82f6',
            'font_color': 'white'
        })
        
        money_format = workbook.add_format({
            'num_format': '#,##0',
            'align': 'right'
        })
        
        percent_format = workbook.add_format({
            'num_format': '0.00%',
            'align': 'right'
        })
        
        # Summary Sheet
        summary_sheet = workbook.add_worksheet('Ringkasan Eksekutif')
        summary_sheet.set_column('A:A', 25)
        summary_sheet.set_column('B:B', 20)
        
        row = 0
        summary_sheet.write(row, 0, 'LAPORAN RINGKASAN EKSEKUTIF', header_format)
        summary_sheet.write(row, 1, '', header_format)
        row += 2
        
        summary_sheet.write(row, 0, 'Periode:')
        summary_sheet.write(row, 1, f"{data.get('period_start', datetime.now()).strftime('%d/%m/%Y')} - {data.get('period_end', datetime.now()).strftime('%d/%m/%Y')}")
        row += 2
        
        summary_sheet.write(row, 0, 'Total Pendapatan', subheader_format)
        summary_sheet.write(row, 1, data.get('total_revenue', 0), money_format)
        row += 1
        
        summary_sheet.write(row, 0, 'Total Pengeluaran', subheader_format)
        summary_sheet.write(row, 1, data.get('total_expenses', 0), money_format)
        row += 1
        
        summary_sheet.write(row, 0, 'Laba Bersih', subheader_format)
        summary_sheet.write(row, 1, data.get('net_profit', 0), money_format)
        row += 1
        
        summary_sheet.write(row, 0, 'Margin Keuntungan', subheader_format)
        summary_sheet.write(row, 1, data.get('overall_profit_margin', 0) / 100, percent_format)
        row += 2
        
        # Business Units Sheet
        if data.get('business_units'):
            bu_sheet = workbook.add_worksheet('Kinerja Unit Bisnis')
            bu_sheet.set_column('A:A', 25)
            bu_sheet.set_column('B:F', 15)
            
            headers = ['Unit Bisnis', 'Pendapatan', 'Pengeluaran', 'Laba Bersih', 'Margin (%)', 'Total Orders']
            for col, header in enumerate(headers):
                bu_sheet.write(0, col, header, subheader_format)
            
            for idx, bu in enumerate(data['business_units'], start=1):
                bu_sheet.write(idx, 0, bu['business_name'])
                bu_sheet.write(idx, 1, bu['total_revenue'], money_format)
                bu_sheet.write(idx, 2, bu['total_expenses'], money_format)
                bu_sheet.write(idx, 3, bu['net_profit'], money_format)
                bu_sheet.write(idx, 4, bu['profit_margin'] / 100, percent_format)
                bu_sheet.write(idx, 5, bu['total_orders'])
        
        workbook.close()
        buffer.seek(0)
        return buffer
    
    def generate_ppob_shift_excel(self, data: Dict[str, Any]) -> BytesIO:
        """Generate PPOB Shift Report in Excel format"""
        buffer = BytesIO()
        workbook = xlsxwriter.Workbook(buffer, {'in_memory': True})
        worksheet = workbook.add_worksheet('Laporan Shift PPOB')
        
        # Formats
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'bg_color': '#1e40af',
            'font_color': 'white',
            'align': 'center'
        })
        
        subheader_format = workbook.add_format({
            'bold': True,
            'bg_color': '#3b82f6',
            'font_color': 'white'
        })
        
        money_format = workbook.add_format({
            'num_format': '#,##0',
            'align': 'right'
        })
        
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:E', 15)
        
        row = 0
        worksheet.write(row, 0, 'LAPORAN SHIFT PPOB', header_format)
        worksheet.merge_range(row, 0, row, 4, 'LAPORAN SHIFT PPOB', header_format)
        row += 2
        
        worksheet.write(row, 0, 'Tanggal:')
        worksheet.write(row, 1, data.get('report_date', datetime.now()).strftime('%d/%m/%Y'))
        row += 1
        
        worksheet.write(row, 0, 'Shift:')
        worksheet.write(row, 1, f"Shift {data.get('shift', 1)}")
        row += 1
        
        worksheet.write(row, 0, 'Petugas:')
        worksheet.write(row, 1, data.get('petugas_name', '-'))
        row += 2
        
        # Product breakdown header
        headers = ['Jenis Produk', 'Jumlah Transaksi', 'Total Amount', 'Fee', 'Komisi']
        for col, header in enumerate(headers):
            worksheet.write(row, col, header, subheader_format)
        row += 1
        
        # Product data
        for product in data.get('product_breakdown', []):
            worksheet.write(row, 0, product['product_type'])
            worksheet.write(row, 1, product['transaction_count'])
            worksheet.write(row, 2, product['total_amount'], money_format)
            worksheet.write(row, 3, product['total_fee'], money_format)
            worksheet.write(row, 4, product['total_commission'], money_format)
            row += 1
        
        # Totals
        total_format = workbook.add_format({'bold': True, 'bg_color': '#dbeafe'})
        worksheet.write(row, 0, 'TOTAL', total_format)
        worksheet.write(row, 1, data.get('total_transactions', 0), total_format)
        worksheet.write(row, 2, data.get('total_amount', 0), money_format)
        worksheet.write(row, 3, data.get('total_fee', 0), money_format)
        worksheet.write(row, 4, data.get('total_commission', 0), money_format)
        
        workbook.close()
        buffer.seek(0)
        return buffer


# Create singleton instance
report_generator = ReportGenerator()
