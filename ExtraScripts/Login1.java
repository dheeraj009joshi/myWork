import java.awt.*;
import java.util.ArrayList;
import java.util.List;
import javax.swing.*;

public class Login1 {

    private static List<User> users = new ArrayList<>();

    public static void main(String[] args) {
        JFrame frame = new JFrame("Login and Signup");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(400, 300);

        // Panel
        JPanel panel = new JPanel();
        panel.setLayout(new CardLayout());

        // Login Components
        JPanel loginPanel = new JPanel(new GridLayout(3, 2));
        JLabel loginLabel = new JLabel("Username:");
        JTextField loginUsername = new JTextField();
        JLabel passLabel = new JLabel("Password:");
        JPasswordField loginPassword = new JPasswordField();
        JButton loginButton = new JButton("Login");
        JButton goToSignupButton = new JButton("Go to Signup");

        loginPanel.add(loginLabel);
        loginPanel.add(loginUsername);
        loginPanel.add(passLabel);
        loginPanel.add(loginPassword);
        loginPanel.add(loginButton);
        loginPanel.add(goToSignupButton);

        // Signup Components
        JPanel signupPanel = new JPanel(new GridLayout(4, 2));
        JLabel signupUserLabel = new JLabel("Username:");
        JTextField signupUsername = new JTextField();
        JLabel signupEmailLabel = new JLabel("Email:");
        JTextField signupEmail = new JTextField();
        JLabel signupPassLabel = new JLabel("Password:");
        JPasswordField signupPassword = new JPasswordField();
        JButton signupButton = new JButton("Signup");
        JButton goToLoginButton = new JButton("Go to Login");

        signupPanel.add(signupUserLabel);
        signupPanel.add(signupUsername);
        signupPanel.add(signupEmailLabel);
        signupPanel.add(signupEmail);
        signupPanel.add(signupPassLabel);
        signupPanel.add(signupPassword);
        signupPanel.add(signupButton);
        signupPanel.add(goToLoginButton);

        panel.add(loginPanel, "Login");
        panel.add(signupPanel, "Signup");

        frame.add(panel);

        // Login Button Listener
        loginButton.addActionListener(e -> {
            String username = loginUsername.getText();
            String password = String.valueOf(loginPassword.getPassword());
            boolean isValid = users.stream()
                    .anyMatch(user -> user.getUsername().equals(username) && user.getPassword().equals(password));
            if (isValid) {
                JOptionPane.showMessageDialog(frame, "Login Successful");
            } else {
                JOptionPane.showMessageDialog(frame, "Invalid Credentials");
            }
        });

        // Signup Button Listener
        signupButton.addActionListener(e -> {
            String username = signupUsername.getText();
            String email = signupEmail.getText();
            String password = String.valueOf(signupPassword.getPassword());
            boolean exists = users.stream().anyMatch(user -> user.getUsername().equals(username));
            if (exists) {
                JOptionPane.showMessageDialog(frame, "Username already exists!");
            } else {
                users.add(new User(username, email, password));
                JOptionPane.showMessageDialog(frame, "Signup Successful");
            }
        });

        // Navigation Listeners
        goToSignupButton.addActionListener(e -> {
            CardLayout cl = (CardLayout) (panel.getLayout());
            cl.show(panel, "Signup");
        });

        goToLoginButton.addActionListener(e -> {
            CardLayout cl = (CardLayout) (panel.getLayout());
            cl.show(panel, "Login");
        });

        frame.setVisible(true);
    }

    static class User {
        private String username;
        private String email;
        private String password;

        public User(String username, String email, String password) {
            this.username = username;
            this.email = email;
            this.password = password;
        }

        public String getUsername() {
            return username;
        }

        public String getPassword() {
            return password;
        }
    }
}
