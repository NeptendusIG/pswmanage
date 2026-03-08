
#############################
#     Project name      #
#      Class name       #
#        Date//         #
#############################
# NOTES :
"""

"""
# IMPORTS
import os, sys
if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging
import tkinter as tk
import ttkbootstrap as ttk

# SETTINGS
logger = logging.getLogger('debugging')


class SuggestionsEntry(tk.Entry):
    def __init__(self, master, suggestions, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.suggestions = suggestions
        self.listbox = None
        self.bind("<FocusIn>", self.show_suggestions)

    def show_suggestions(self, event):
        if self.listbox:
            self.listbox.destroy()

        # Filtrer les suggestions
        current_text = self.get()
        if not current_text:
            matches = self.suggestions
        else:
            matches = [s for s in self.suggestions if s.startswith(current_text)]
        
        # Créer une liste déroulante
        if matches:
            self.listbox = tk.Listbox(self.master, height=len(matches), bg="white", selectmode=tk.SINGLE)
            self.listbox.bind("<ButtonRelease-1>", self.select_suggestion)
            self.listbox.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
            for match in matches:
                self.listbox.insert(tk.END, match)

    def select_suggestion(self, event):
        # Remplir l'`Entry` avec la suggestion sélectionnée
        if self.listbox:
            self.delete(0, tk.END)
            self.insert(0, self.listbox.get(tk.ACTIVE))
            self.listbox.destroy()
            self.listbox = None



if __name__ == '__main__':
    # tests
    root = tk.Tk()
    root.title("Auto-complétion avec Liste Déroulante")

    suggestions = ["apple", "banana", "cherry", "date", "fig", "grape", "kiwi"]
    entry = SuggestionsEntry(root, suggestions, width=30)
    entry.pack(pady=10, padx=10)

    root.mainloop()

