package com.example.cie_que1

import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.widget.TextView

class SecondActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_second)

        // Get the book name passed from MainActivity
        val bookName = intent.getStringExtra("book_name")

        // Find the TextView in the layout
        val bookText = findViewById<TextView>(R.id.selectedBookText)

        // Set the book name to the TextView
        bookText.text = "Selected Book:\n$bookName"
    }
}
