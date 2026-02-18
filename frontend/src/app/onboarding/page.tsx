"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Mail, Sparkles, BookOpen, ChevronRight, ChevronLeft, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";

const STEPS = [
    {
        id: 1,
        title: "Connect Email",
        icon: Mail,
        description: "Link your Gmail or Outlook account",
    },
    {
        id: 2,
        title: "Set Preferences",
        icon: Sparkles,
        description: "Customize your AI and notification settings",
    },
    {
        id: 3,
        title: "Welcome",
        icon: BookOpen,
        description: "Learn the basics of SortMail",
    },
];

export default function OnboardingPage() {
    const router = useRouter();
    const [currentStep, setCurrentStep] = useState(1);
    const [preferences, setPreferences] = useState({
        aiTone: "normal",
        autoDraft: true,
        emailNotifications: true,
        pushNotifications: true,
    });

    const handleNext = () => {
        if (currentStep < STEPS.length) {
            setCurrentStep(currentStep + 1);
        } else {
            // Complete onboarding
            router.push("/dashboard");
        }
    };

    const handleSkip = () => {
        router.push("/dashboard");
    };

    return (
        <div className="min-h-screen bg-paper flex items-center justify-center p-8">
            <div className="max-w-2xl w-full">
                {/* Progress */}
                <div className="mb-8">
                    <div className="flex items-center justify-between mb-4">
                        {STEPS.map((step, index) => {
                            const Icon = step.icon;
                            const isActive = currentStep === step.id;
                            const isCompleted = currentStep > step.id;
                            return (
                                <div key={step.id} className="flex items-center flex-1">
                                    <div className="flex flex-col items-center">
                                        <div
                                            className={`
                                                w-12 h-12 rounded-full flex items-center justify-center mb-2 transition-colors
                                                ${isCompleted
                                                    ? "bg-success text-white"
                                                    : isActive
                                                        ? "bg-accent text-white"
                                                        : "bg-border text-muted"
                                                }
                                            `}
                                        >
                                            {isCompleted ? <Check className="w-6 h-6" /> : <Icon className="w-6 h-6" />}
                                        </div>
                                        <span className={`text-xs ${isActive ? "text-ink font-medium" : "text-muted"}`}>
                                            {step.title}
                                        </span>
                                    </div>
                                    {index < STEPS.length - 1 && (
                                        <div className={`flex-1 h-0.5 mx-4 ${isCompleted ? "bg-success" : "bg-border"}`} />
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Step Content */}
                <Card className="p-8">
                    {currentStep === 1 && (
                        <div>
                            <h1 className="font-display text-3xl text-ink mb-2">
                                Connect Your Email
                            </h1>
                            <p className="text-muted mb-6">
                                Choose your email provider to get started with SortMail
                            </p>
                            <div className="space-y-3">
                                <Button className="w-full h-14 gap-3 justify-start" variant="outline">
                                    <Mail className="w-5 h-5" />
                                    <span className="font-medium">Continue with Gmail</span>
                                </Button>
                                <Button className="w-full h-14 gap-3 justify-start" variant="outline">
                                    <Mail className="w-5 h-5" />
                                    <span className="font-medium">Continue with Outlook</span>
                                </Button>
                            </div>
                        </div>
                    )}

                    {currentStep === 2 && (
                        <div>
                            <h1 className="font-display text-3xl text-ink mb-2">
                                Set Your Preferences
                            </h1>
                            <p className="text-muted mb-6">
                                Customize how SortMail works for you
                            </p>
                            <div className="space-y-6">
                                <div>
                                    <Label className="text-base font-medium text-ink mb-3 block">
                                        AI Writing Tone
                                    </Label>
                                    <div className="grid grid-cols-3 gap-3">
                                        {["brief", "normal", "formal"].map((tone) => (
                                            <button
                                                key={tone}
                                                onClick={() => setPreferences({ ...preferences, aiTone: tone })}
                                                className={`
                                                    p-3 rounded-lg border-2 transition-all capitalize
                                                    ${preferences.aiTone === tone
                                                        ? "border-accent bg-accent/5"
                                                        : "border-border hover:border-accent/50"
                                                    }
                                                `}
                                            >
                                                {tone}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                                <div className="flex items-center justify-between">
                                    <Label className="text-base font-medium text-ink">Auto-Draft Replies</Label>
                                    <Switch
                                        checked={preferences.autoDraft}
                                        onCheckedChange={(checked) =>
                                            setPreferences({ ...preferences, autoDraft: checked })
                                        }
                                    />
                                </div>
                                <div className="flex items-center justify-between">
                                    <Label className="text-base font-medium text-ink">Email Notifications</Label>
                                    <Switch
                                        checked={preferences.emailNotifications}
                                        onCheckedChange={(checked) =>
                                            setPreferences({ ...preferences, emailNotifications: checked })
                                        }
                                    />
                                </div>
                                <div className="flex items-center justify-between">
                                    <Label className="text-base font-medium text-ink">Push Notifications</Label>
                                    <Switch
                                        checked={preferences.pushNotifications}
                                        onCheckedChange={(checked) =>
                                            setPreferences({ ...preferences, pushNotifications: checked })
                                        }
                                    />
                                </div>
                            </div>
                        </div>
                    )}

                    {currentStep === 3 && (
                        <div>
                            <h1 className="font-display text-3xl text-ink mb-2">
                                Welcome to SortMail!
                            </h1>
                            <p className="text-muted mb-6">
                                You&apos;re all set. Here are some tips to get started:
                            </p>
                            <div className="space-y-4">
                                {[
                                    "Check your Dashboard for AI-generated briefings",
                                    "Review your Inbox for prioritized emails",
                                    "Use Tasks to track action items from emails",
                                    "Set up Follow-ups to never miss important replies",
                                ].map((tip, index) => (
                                    <div key={index} className="flex items-start gap-3">
                                        <div className="w-6 h-6 rounded-full bg-accent/10 text-accent flex items-center justify-center shrink-0 mt-0.5">
                                            <span className="text-xs font-bold">{index + 1}</span>
                                        </div>
                                        <p className="text-ink">{tip}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Navigation */}
                    <div className="flex items-center justify-between mt-8 pt-6 border-t border-border">
                        <Button
                            variant="ghost"
                            onClick={handleSkip}
                            className="text-muted hover:text-ink"
                        >
                            Skip Tutorial
                        </Button>
                        <div className="flex gap-3">
                            {currentStep > 1 && (
                                <Button
                                    variant="outline"
                                    onClick={() => setCurrentStep(currentStep - 1)}
                                    className="gap-2"
                                >
                                    <ChevronLeft className="w-4 h-4" />
                                    Previous
                                </Button>
                            )}
                            <Button onClick={handleNext} className="gap-2">
                                {currentStep === STEPS.length ? "Get Started" : "Next"}
                                {currentStep < STEPS.length && <ChevronRight className="w-4 h-4" />}
                            </Button>
                        </div>
                    </div>
                </Card>
            </div>
        </div>
    );
}
