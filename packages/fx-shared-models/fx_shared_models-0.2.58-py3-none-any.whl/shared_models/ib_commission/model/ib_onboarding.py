"""
IB Onboarding tracking models
"""
from django.db import models
from django.utils import timezone
from shared_models.common.base import BaseModel


class IBOnboardingStatus(BaseModel):
    """
    Track IB onboarding progress through the complete setup process.
    Ensures all required steps are completed before an IB can operate.
    """
    customer = models.OneToOneField(
        'customers.Customer', 
        on_delete=models.CASCADE, 
        related_name='ib_onboarding_status',
        help_text="The IB customer being onboarded"
    )
    
    # Step completion tracking
    ib_account_created = models.BooleanField(
        default=False,
        help_text="IB account has been created in MT5"
    )
    hierarchy_created = models.BooleanField(
        default=False,
        help_text="IB has been positioned in hierarchy (standalone or under parent)"
    )
    agreement_assigned = models.BooleanField(
        default=False,
        help_text="IB has been assigned to at least one commission agreement"
    )
    referral_source_created = models.BooleanField(
        default=False,
        help_text="IB referral code has been created for client onboarding"
    )
    
    # Completion tracking
    completed_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Timestamp when all onboarding steps were completed"
    )
    completed_by = models.ForeignKey(
        'users.CRMUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='completed_ib_onboardings',
        help_text="CRM user who completed the onboarding"
    )
    
    # Store references to created entities
    hierarchy = models.ForeignKey(
        'ib_commission.IBHierarchy', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        help_text="Reference to the created hierarchy entry"
    )
    agreement = models.ForeignKey(
        'ib_commission.IBAgreement', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        help_text="Primary agreement assigned to the IB"
    )
    referral_source = models.ForeignKey(
        'referrals.ReferralSource', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        help_text="Primary referral source created for the IB"
    )
    
    # Additional tracking
    notes = models.TextField(
        blank=True,
        help_text="Any notes or special instructions for this IB's onboarding"
    )
    
    class Meta:
        app_label = 'ib_commission'
        db_table = 'ib_onboarding_status'
        verbose_name = 'IB Onboarding Status'
        verbose_name_plural = 'IB Onboarding Statuses'
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['completed_at']),
            models.Index(fields=['ib_account_created', 'hierarchy_created', 
                               'agreement_assigned', 'referral_source_created']),
        ]
    
    def __str__(self):
        return f"IB Onboarding: {self.customer} - {'Completed' if self.is_completed else 'In Progress'}"
    
    @property
    def is_completed(self):
        """Check if all onboarding steps are completed"""
        return all([
            self.ib_account_created,
            self.hierarchy_created,
            self.agreement_assigned,
            self.referral_source_created
        ])
    
    @property
    def completion_percentage(self):
        """Calculate the percentage of completed steps"""
        steps = [
            self.ib_account_created,
            self.hierarchy_created,
            self.agreement_assigned,
            self.referral_source_created
        ]
        completed = sum(1 for step in steps if step)
        return (completed / len(steps)) * 100
    
    @property
    def next_step(self):
        """Determine the next required step in the onboarding process"""
        if not self.ib_account_created:
            return 'ib_account'
        elif not self.hierarchy_created:
            return 'hierarchy'
        elif not self.agreement_assigned:
            return 'agreement'
        elif not self.referral_source_created:
            return 'referral_source'
        else:
            return None
    
    @property
    def missing_steps(self):
        """Get a list of incomplete steps"""
        steps = []
        if not self.ib_account_created:
            steps.append('ib_account')
        if not self.hierarchy_created:
            steps.append('hierarchy')
        if not self.agreement_assigned:
            steps.append('agreement')
        if not self.referral_source_created:
            steps.append('referral_source')
        return steps
    
    def mark_completed(self, user=None):
        """Mark the onboarding as completed if all steps are done"""
        if self.is_completed and not self.completed_at:
            self.completed_at = timezone.now()
            if user:
                self.completed_by = user
            self.save(update_fields=['completed_at', 'completed_by'])
            return True
        return False
    
    def update_step(self, step_name, completed=True, reference=None, user=None):
        """
        Update a specific onboarding step
        
        Args:
            step_name: One of 'ib_account', 'hierarchy', 'agreement', 'referral_source'
            completed: Whether the step is completed
            reference: The related object (hierarchy, agreement, or referral_source)
            user: The user completing the step
        """
        update_fields = []
        
        if step_name == 'ib_account':
            self.ib_account_created = completed
            update_fields.append('ib_account_created')
            
        elif step_name == 'hierarchy' and reference:
            self.hierarchy_created = completed
            self.hierarchy = reference
            update_fields.extend(['hierarchy_created', 'hierarchy'])
            
        elif step_name == 'agreement' and reference:
            self.agreement_assigned = completed
            self.agreement = reference
            update_fields.extend(['agreement_assigned', 'agreement'])
            
        elif step_name == 'referral_source' and reference:
            self.referral_source_created = completed
            self.referral_source = reference
            update_fields.extend(['referral_source_created', 'referral_source'])
        
        if update_fields:
            self.save(update_fields=update_fields)
            
            # Check if all steps are now completed
            if self.is_completed and not self.completed_at:
                self.mark_completed(user)
                
        return self.is_completed