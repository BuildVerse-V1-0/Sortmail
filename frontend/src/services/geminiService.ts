
import { Email } from '@/types/dashboard';

export const generateBriefing = async (emails: Email[]): Promise<string> => {
    // Mock simulation
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve("- 3 High priority emails require immediate action relating to Q3 goals.\n- Marketing campaign approval pending for 'Winter Glow'.\n- Server CPU usage alert resolved automatically.");
        }, 1200);
    });
};

export const analyzeEmailContent = async (body: string, sender: string, subject: string) => {
    // Mock simulation
    return new Promise<{ summary: string[], actionItems: string[] }>((resolve) => {
        setTimeout(() => {
            resolve({
                summary: [
                    `Key topic: ${subject}`,
                    `Sender ${sender} is requesting updates.`,
                    "Urgency detected in tone."
                ],
                actionItems: [
                    "Reply to sender",
                    "Schedule follow-up meeting",
                    "Review attached documents"
                ]
            });
        }, 1000);
    });
};

export const generateDraftReply = async (email: Email, tone: string) => {
    return new Promise<string>((resolve) => {
        setTimeout(() => {
            resolve(`Hi ${email.sender.split(' ')[0]},\n\nThis is a generated ${tone} reply draft acknowledging the receipt of "${email.subject}".\n\nBest,\nUser`);
        }, 800);
    });
};
