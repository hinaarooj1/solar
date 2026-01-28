import { NextRequest, NextResponse } from 'next/server';
import { getEmailService } from '@/lib/email-service';

export async function GET(request: NextRequest) {
  try {
    const emailService = getEmailService();
    const success = await emailService.sendTestEmail();
    
    const recipient = process.env.ALERT_EMAIL || 'configured email';
    
    if (success) {
      return NextResponse.json({
        success: true,
        message: "Test email sent successfully",
        recipient: recipient
      });
    } else {
      return NextResponse.json({
        success: false,
        message: "Failed to send email - check configuration",
        recipient: recipient
      }, { status: 400 });
    }
  } catch (error: any) {
    console.error('Error in /api/notifications/test-email:', error.message);
    return NextResponse.json({
      success: false, 
      message: error.message,
      recipient: process.env.ALERT_EMAIL || 'configured email'
    }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  return GET(request);
}
