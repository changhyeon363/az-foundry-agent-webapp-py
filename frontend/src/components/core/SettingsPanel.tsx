import React from 'react';
import {
  Drawer,
  DrawerHeader,
  DrawerHeaderTitle,
  DrawerBody,
  Button,
  Divider,
  makeStyles,
  tokens,
} from '@fluentui/react-components';
import { Dismiss24Regular, SignOutRegular } from '@fluentui/react-icons';
import { ThemePicker } from './ThemePicker';

interface SettingsPanelProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onLogout?: () => void;
}

const useStyles = makeStyles({
  drawer: {
    width: '320px',
  },
  section: {
    marginBottom: tokens.spacingVerticalXXL,
  },
  sectionTitle: {
    fontSize: tokens.fontSizeBase300,
    fontWeight: tokens.fontWeightSemibold,
    marginBottom: tokens.spacingVerticalM,
    color: tokens.colorNeutralForeground1,
  },
  logoutSection: {
    marginTop: 'auto',
    paddingTop: tokens.spacingVerticalL,
  },
  logoutButton: {
    width: '100%',
  },
});

export const SettingsPanel: React.FC<SettingsPanelProps> = ({ isOpen, onOpenChange, onLogout }) => {
  const styles = useStyles();

  const handleLogout = () => {
    onOpenChange(false);
    onLogout?.();
  };

  return (
    <Drawer
      open={isOpen}
      onOpenChange={(_, { open }) => onOpenChange(open)}
      position="end"
      className={styles.drawer}
    >
      <DrawerHeader>
        <DrawerHeaderTitle
          action={
            <Button
              appearance="subtle"
              aria-label="Close"
              icon={<Dismiss24Regular />}
              onClick={() => onOpenChange(false)}
            />
          }
        >
          Settings
        </DrawerHeaderTitle>
      </DrawerHeader>

      <DrawerBody>
        <div className={styles.section}>
          <div className={styles.sectionTitle}>Appearance</div>
          <ThemePicker />
        </div>

        {onLogout && (
          <>
            <Divider />
            <div className={styles.logoutSection}>
              <Button
                className={styles.logoutButton}
                appearance="secondary"
                icon={<SignOutRegular />}
                onClick={handleLogout}
              >
                Sign Out
              </Button>
            </div>
          </>
        )}
      </DrawerBody>
    </Drawer>
  );
};
