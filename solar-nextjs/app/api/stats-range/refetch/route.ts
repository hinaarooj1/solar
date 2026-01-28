import { NextRequest, NextResponse } from 'next/server';
import { getWatchPowerAPISync } from '@/lib/watchpower-api';

/**
 * Retry helper with exponential backoff
 */
async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  initialDelay: number = 1000
): Promise<T> {
  let lastError: Error;
  
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error: any) {
      lastError = error;
      
      // Don't retry on certain errors (like no data available)
      if (error.message?.includes('No data available') || error.message?.includes('ERR_NO_RECORD')) {
        throw error;
      }
      
      // If this is the last attempt, throw the error
      if (attempt === maxRetries - 1) {
        throw error;
      }
      
      // Exponential backoff: 1s, 2s, 4s
      const delay = initialDelay * Math.pow(2, attempt);
      console.log(`⚠️ Retry attempt ${attempt + 1}/${maxRetries} after ${delay}ms for error: ${error.message}`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  throw lastError!;
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { dates } = body;

    if (!dates || !Array.isArray(dates) || dates.length === 0) {
      return NextResponse.json(
        { success: false, error: 'dates array is required' },
        { status: 400 }
      );
    }

    const api = getWatchPowerAPISync();
    const results: any[] = [];
    const intervalHours = 5 / 60; // 5 minutes

    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      async start(controller) {
        try {
          for (let i = 0; i < dates.length; i++) {
            const dateStr = dates[i];
            let dailyData: any;

            try {
              console.log(`🔄 Refetching ${dateStr} (${i + 1}/${dates.length})...`);

              // Use retry logic for API calls
              const data = await retryWithBackoff(
                () => api.getDailyData(dateStr),
                3, // max 3 retries
                1000 // initial delay 1 second
              );

              const rows = data?.dat?.row || [];

              // Check if we have any valid data for this date
              if (rows.length === 0) {
                dailyData = {
                  date: dateStr,
                  production_kwh: null,
                  load_kwh: null,
                  success: false,
                  error: 'No data available'
                };
              } else {
                let pvWh = 0;
                let loadWh = 0;
                let hasValidData = false;

                for (const rec of rows) {
                  const fields = rec?.field || [];
                  if (fields.length < 22) continue;

                  const timestamp = fields[1];
                  if (!timestamp?.startsWith(dateStr)) continue;

                  const pvPower = parseFloat(fields[11]) || 0;
                  const loadPower = parseFloat(fields[21]) || 0;
                  pvWh += pvPower * intervalHours;
                  loadWh += loadPower * intervalHours;
                  hasValidData = true;
                }

                if (!hasValidData) {
                  dailyData = {
                    date: dateStr,
                    production_kwh: null,
                    load_kwh: null,
                    success: false,
                    error: 'No valid records found'
                  };
                } else {
                  dailyData = {
                    date: dateStr,
                    production_kwh: Math.round((pvWh / 1000) * 100) / 100,
                    load_kwh: Math.round((loadWh / 1000) * 100) / 100,
                    success: true
                  };
                }
              }

            } catch (error: any) {
              console.error(`❌ Error refetching ${dateStr}:`, error.message);
              dailyData = {
                date: dateStr,
                production_kwh: null,
                load_kwh: null,
                success: false,
                error: error.message
              };
            }

            results.push(dailyData);

            // Send progress update
            const progress = ((i + 1) / dates.length) * 100;
            const progressResponse = JSON.stringify({
              success: true,
              progress: Math.round(progress * 100) / 100,
              daily: dailyData,
              completed: i + 1,
              total: dates.length
            }) + "\n";

            controller.enqueue(encoder.encode(progressResponse));
          }

          controller.close();
        } catch (error: any) {
          console.error('Error in refetch stream:', error.message);
          const errorResponse = JSON.stringify({
            success: false,
            error: error.message
          }) + "\n";
          controller.enqueue(encoder.encode(errorResponse));
          controller.close();
        }
      }
    });

    return new Response(stream, {
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      }
    });

  } catch (error: any) {
    console.error('Error in /api/stats-range/refetch:', error.message);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}
