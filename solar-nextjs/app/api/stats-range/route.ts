import { NextRequest } from 'next/server';
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

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const fromDate = searchParams.get('from_date');
  const toDate = searchParams.get('to_date');

  if (!fromDate || !toDate) {
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        const errorResponse = JSON.stringify({ 
          success: false, 
          error: "from_date and to_date are required" 
        }) + "\n";
        controller.enqueue(encoder.encode(errorResponse));
        controller.close();
      }
    });
    return new Response(stream, {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      try {
        const api = getWatchPowerAPISync();
        const start = new Date(fromDate);
        const end = new Date(toDate);

        if (start > end) {
          const errorResponse = JSON.stringify({ 
            success: false, 
            error: "from_date must be <= to_date" 
          }) + "\n";
          controller.enqueue(encoder.encode(errorResponse));
          controller.close();
          return;
        }

        const totalDays = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1;
        let totalProdWh = 0;
        let totalLoadWh = 0;
        const dailyStats: any[] = [];

        const current = new Date(start);
        while (current <= end) {
          let dailyData: any;
          
          try {
            const dateStr = current.toISOString().split('T')[0];
            console.log(`📊 Processing ${dateStr}...`);
            
            // Use retry logic for API calls
            const data = await retryWithBackoff(
              () => api.getDailyData(dateStr),
              3, // max 3 retries
              1000 // initial delay 1 second
            );

            const rows = data?.dat?.row || [];
            
            // Check if we have any valid data for this date
            if (rows.length === 0) {
              // No data available for this date
              dailyData = {
                date: dateStr,
                production_kwh: null,
                load_kwh: null
              };
            } else {
              let pvWh = 0;
              let loadWh = 0;
              const intervalHours = 5 / 60; // 5 minutes
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
                // No valid records for this date
                dailyData = {
                  date: dateStr,
                  production_kwh: null,
                  load_kwh: null
                };
              } else {
                totalProdWh += pvWh;
                totalLoadWh += loadWh;

                dailyData = {
                  date: dateStr,
                  production_kwh: Math.round((pvWh / 1000) * 100) / 100,
                  load_kwh: Math.round((loadWh / 1000) * 100) / 100
                };
              }
            }

          } catch (error: any) {
            console.error(`❌ Error processing ${current.toISOString().split('T')[0]}:`, error.message);
            dailyData = {
              date: current.toISOString().split('T')[0],
              production_kwh: null,
              load_kwh: null,
              error: error.message
            };
          }

          dailyStats.push(dailyData);

          // Send progress update (matching Python backend format)
          const progress = (dailyStats.length / totalDays) * 100;
          const progressResponse = JSON.stringify({
            success: true,
            progress: Math.round(progress * 100) / 100,
            daily: dailyData,
            total_production_kwh: Math.round((totalProdWh / 1000) * 100) / 100,
            total_load_kwh: Math.round((totalLoadWh / 1000) * 100) / 100
          }) + "\n";
          
          controller.enqueue(encoder.encode(progressResponse));

          current.setDate(current.getDate() + 1);
        }

        controller.close();
        
      } catch (error: any) {
        console.error('Error in /api/stats-range:', error.message);
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
}
