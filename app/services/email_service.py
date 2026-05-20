import resend
from app.core.config import settings

resend.api_key = settings.RESEND_API_KEY


class EmailService:

    def _send(self, to: str, subject: str, html: str) -> bool:
        if not settings.RESEND_API_KEY:
            print(f"Email not sent (no API key): {subject} to {to}")
            return False
        try:
            resend.Emails.send({
                "from": settings.EMAIL_FROM,
                "to": to,
                "subject": subject,
                "html": html,
            })
            return True
        except Exception as e:
            print(f"Email send failed: {e}")
            return False

    def send_welcome_email(self, to: str, name: str, workspace_name: str) -> bool:
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #6366f1; padding: 24px; border-radius: 8px 8px 0 0;">
                <h1 style="color: white; margin: 0;">Welcome to Flowspace</h1>
            </div>
            <div style="background: #f9fafb; padding: 24px; border-radius: 0 0 8px 8px;">
                <p style="color: #374151;">Hi {name},</p>
                <p style="color: #374151;">Your workspace <strong>{workspace_name}</strong> has been created successfully.</p>
                <p style="color: #374151;">You can now create projects, invite team members, and manage tasks.</p>
                <a href="{settings.FRONTEND_URL}"
                   style="display: inline-block; background: #6366f1; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; margin-top: 16px;">
                    Go to Flowspace
                </a>
                <p style="color: #9ca3af; font-size: 12px; margin-top: 24px;">The Flowspace Team</p>
            </div>
        </div>
        """
        return self._send(to, f"Welcome to Flowspace — {workspace_name} is ready", html)

    def send_invite_email(
        self,
        to: str,
        invited_by: str,
        workspace_name: str,
        temp_password: str,
        tenant_slug: str,
    ) -> bool:
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #6366f1; padding: 24px; border-radius: 8px 8px 0 0;">
                <h1 style="color: white; margin: 0;">You have been invited</h1>
            </div>
            <div style="background: #f9fafb; padding: 24px; border-radius: 0 0 8px 8px;">
                <p style="color: #374151;"><strong>{invited_by}</strong> has invited you to join <strong>{workspace_name}</strong> on Flowspace.</p>
                <div style="background: #e0e7ff; padding: 16px; border-radius: 6px; margin: 16px 0;">
                    <p style="color: #374151; margin: 0 0 8px 0;"><strong>Your login details:</strong></p>
                    <p style="color: #374151; margin: 4px 0;">Email: <strong>{to}</strong></p>
                    <p style="color: #374151; margin: 4px 0;">Temporary Password: <strong>{temp_password}</strong></p>
                    <p style="color: #374151; margin: 4px 0;">Workspace slug: <strong>{tenant_slug}</strong></p>
                </div>
                <p style="color: #ef4444; font-size: 14px;">You will be required to change your password on first login.</p>
                <a href="{settings.FRONTEND_URL}/login"
                   style="display: inline-block; background: #6366f1; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; margin-top: 8px;">
                    Accept Invitation
                </a>
                <p style="color: #9ca3af; font-size: 12px; margin-top: 24px;">The Flowspace Team</p>
            </div>
        </div>
        """
        return self._send(to, f"You have been invited to {workspace_name} on Flowspace", html)

    def send_task_assigned_email(
        self,
        to: str,
        assignee_name: str,
        task_title: str,
        assigned_by: str,
        project_name: str,
    ) -> bool:
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #6366f1; padding: 24px; border-radius: 8px 8px 0 0;">
                <h1 style="color: white; margin: 0;">Task Assigned to You</h1>
            </div>
            <div style="background: #f9fafb; padding: 24px; border-radius: 0 0 8px 8px;">
                <p style="color: #374151;">Hi {assignee_name},</p>
                <p style="color: #374151;"><strong>{assigned_by}</strong> assigned you a task in <strong>{project_name}</strong>:</p>
                <div style="background: #e0e7ff; padding: 16px; border-radius: 6px; margin: 16px 0;">
                    <p style="color: #374151; margin: 0; font-size: 16px;"><strong>{task_title}</strong></p>
                </div>
                <a href="{settings.FRONTEND_URL}"
                   style="display: inline-block; background: #6366f1; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none;">
                    View Task
                </a>
                <p style="color: #9ca3af; font-size: 12px; margin-top: 24px;">The Flowspace Team</p>
            </div>
        </div>
        """
        return self._send(to, f"New task assigned: {task_title}", html)

    def send_comment_notification_email(
        self,
        to: str,
        recipient_name: str,
        commenter_name: str,
        task_title: str,
        comment_body: str,
        project_name: str,
    ) -> bool:
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #6366f1; padding: 24px; border-radius: 8px 8px 0 0;">
                <h1 style="color: white; margin: 0;">New Comment on Your Task</h1>
            </div>
            <div style="background: #f9fafb; padding: 24px; border-radius: 0 0 8px 8px;">
                <p style="color: #374151;">Hi {recipient_name},</p>
                <p style="color: #374151;"><strong>{commenter_name}</strong> commented on <strong>{task_title}</strong> in <strong>{project_name}</strong>:</p>
                <div style="background: #f3f4f6; padding: 16px; border-radius: 6px; margin: 16px 0; border-left: 4px solid #6366f1;">
                    <p style="color: #374151; margin: 0;">{comment_body}</p>
                </div>
                <a href="{settings.FRONTEND_URL}"
                   style="display: inline-block; background: #6366f1; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none;">
                    View Task
                </a>
                <p style="color: #9ca3af; font-size: 12px; margin-top: 24px;">The Flowspace Team</p>
            </div>
        </div>
        """
        return self._send(to, f"New comment on: {task_title}", html)

    def send_password_reset_email(
        self,
        to: str,
        name: str,
        reset_token: str,
    ) -> bool:
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #6366f1; padding: 24px; border-radius: 8px 8px 0 0;">
                <h1 style="color: white; margin: 0;">Reset Your Password</h1>
            </div>
            <div style="background: #f9fafb; padding: 24px; border-radius: 0 0 8px 8px;">
                <p style="color: #374151;">Hi {name},</p>
                <p style="color: #374151;">We received a request to reset your password. Click the button below to set a new password:</p>
                <a href="{reset_url}"
                   style="display: inline-block; background: #6366f1; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; margin: 16px 0;">
                    Reset Password
                </a>
                <p style="color: #374151;">This link expires in 1 hour.</p>
                <p style="color: #374151;">If you did not request a password reset, you can safely ignore this email.</p>
                <p style="color: #9ca3af; font-size: 12px; margin-top: 24px;">The Flowspace Team</p>
            </div>
        </div>
        """
        return self._send(to, "Reset your Flowspace password", html)

    def send_overdue_digest_email(
        self,
        to: str,
        name: str,
        overdue_tasks: list[dict],
        workspace_name: str,
    ) -> bool:
        task_rows = ""
        for task in overdue_tasks:
            task_rows += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #e5e7eb; color: #374151;">{task['title']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #e5e7eb; color: #ef4444;">{task['due_date']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #e5e7eb; color: #374151;">{task['project']}</td>
            </tr>
            """
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #ef4444; padding: 24px; border-radius: 8px 8px 0 0;">
                <h1 style="color: white; margin: 0;">Overdue Tasks Digest</h1>
            </div>
            <div style="background: #f9fafb; padding: 24px; border-radius: 0 0 8px 8px;">
                <p style="color: #374151;">Hi {name},</p>
                <p style="color: #374151;">You have <strong>{len(overdue_tasks)}</strong> overdue tasks in <strong>{workspace_name}</strong>:</p>
                <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
                    <thead>
                        <tr style="background: #f3f4f6;">
                            <th style="padding: 8px; text-align: left; color: #374151;">Task</th>
                            <th style="padding: 8px; text-align: left; color: #374151;">Due Date</th>
                            <th style="padding: 8px; text-align: left; color: #374151;">Project</th>
                        </tr>
                    </thead>
                    <tbody>
                        {task_rows}
                    </tbody>
                </table>
                <a href="{settings.FRONTEND_URL}"
                   style="display: inline-block; background: #6366f1; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none;">
                    View Tasks
                </a>
                <p style="color: #9ca3af; font-size: 12px; margin-top: 24px;">The Flowspace Team</p>
            </div>
        </div>
        """
        return self._send(to, f"You have {len(overdue_tasks)} overdue tasks in {workspace_name}", html)