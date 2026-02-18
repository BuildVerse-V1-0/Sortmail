"use client";

import React, { useState } from "react";
import { Sparkles, Save } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";

export default function SettingsAIPage() {
    const [settings, setSettings] = useState({
        model: "gpt-4",
        tone: "normal",
        autoDraft: true,
        summaryLength: 50,
    });

    const handleSave = () => {
        // Save settings
        console.log("Saving AI settings:", settings);
    };

    return (
        <div className="max-w-4xl">
            <div className="mb-6">
                <h1 className="font-display text-2xl text-ink mb-2">AI Settings</h1>
                <p className="text-muted">
                    Customize how SortMail&apos;s AI processes your emails and generates content.
                </p>
            </div>

            <div className="space-y-6">
                {/* AI Model */}
                <Card className="p-6">
                    <div className="mb-4">
                        <h3 className="font-medium text-ink mb-1">AI Model</h3>
                        <p className="text-sm text-muted">
                            Choose the AI model for email processing
                        </p>
                    </div>
                    <div className="grid grid-cols-3 gap-3">
                        {[
                            { id: "gpt-4", name: "GPT-4", desc: "Most capable" },
                            { id: "gpt-3.5", name: "GPT-3.5", desc: "Faster" },
                            { id: "claude", name: "Claude", desc: "Alternative" },
                        ].map((model) => (
                            <button
                                key={model.id}
                                onClick={() => setSettings({ ...settings, model: model.id })}
                                className={`
                                    p-4 rounded-lg border-2 transition-all text-left
                                    ${settings.model === model.id
                                        ? "border-accent bg-accent/5"
                                        : "border-border hover:border-accent/50"
                                    }
                                `}
                            >
                                <div className="font-medium text-ink mb-1">{model.name}</div>
                                <div className="text-xs text-muted">{model.desc}</div>
                            </button>
                        ))}
                    </div>
                </Card>

                {/* Tone Preferences */}
                <Card className="p-6">
                    <div className="mb-4">
                        <h3 className="font-medium text-ink mb-1">Writing Tone</h3>
                        <p className="text-sm text-muted">
                            Default tone for AI-generated drafts
                        </p>
                    </div>
                    <div className="grid grid-cols-3 gap-3">
                        {[
                            { id: "brief", name: "Brief", desc: "Short & direct" },
                            { id: "normal", name: "Normal", desc: "Balanced" },
                            { id: "formal", name: "Formal", desc: "Professional" },
                        ].map((tone) => (
                            <button
                                key={tone.id}
                                onClick={() => setSettings({ ...settings, tone: tone.id })}
                                className={`
                                    p-4 rounded-lg border-2 transition-all text-left
                                    ${settings.tone === tone.id
                                        ? "border-accent bg-accent/5"
                                        : "border-border hover:border-accent/50"
                                    }
                                `}
                            >
                                <div className="font-medium text-ink mb-1">{tone.name}</div>
                                <div className="text-xs text-muted">{tone.desc}</div>
                            </button>
                        ))}
                    </div>
                </Card>

                {/* Auto-Draft */}
                <Card className="p-6">
                    <div className="flex items-start justify-between">
                        <div className="flex-1">
                            <h3 className="font-medium text-ink mb-1">Auto-Draft Replies</h3>
                            <p className="text-sm text-muted">
                                Automatically generate draft replies for incoming emails
                            </p>
                        </div>
                        <Switch
                            checked={settings.autoDraft}
                            onCheckedChange={(checked) =>
                                setSettings({ ...settings, autoDraft: checked })
                            }
                        />
                    </div>
                </Card>

                {/* Summary Length */}
                <Card className="p-6">
                    <div className="mb-4">
                        <Label className="font-medium text-ink mb-1">Summary Length</Label>
                        <p className="text-sm text-muted">
                            Adjust the length of AI-generated email summaries
                        </p>
                    </div>
                    <div className="space-y-4">
                        <Slider
                            value={[settings.summaryLength]}
                            onValueChange={([value]) =>
                                setSettings({ ...settings, summaryLength: value })
                            }
                            min={20}
                            max={100}
                            step={10}
                            className="w-full"
                        />
                        <div className="flex justify-between text-xs text-muted">
                            <span>Concise</span>
                            <span>{settings.summaryLength}%</span>
                            <span>Detailed</span>
                        </div>
                    </div>
                </Card>

                {/* Save Button */}
                <div className="flex justify-end">
                    <Button onClick={handleSave} className="gap-2">
                        <Save className="w-4 h-4" />
                        Save Settings
                    </Button>
                </div>
            </div>
        </div>
    );
}
