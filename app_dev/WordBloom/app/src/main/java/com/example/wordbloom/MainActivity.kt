package com.example.wordbloom

import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val tvWord = findViewById<TextView>(R.id.tvWord)
        val tvMeaning = findViewById<TextView>(R.id.tvMeaning)
        val tvExample = findViewById<TextView>(R.id.tvExample)
        val btnNewWord = findViewById<Button>(R.id.btnNewWord)

        val words = listOf(
            Triple("Resilient", "Able to recover quickly", "She is resilient in difficult times."),
            Triple("Curious", "Eager to learn", "He is curious about technology."),
            Triple("Consistent", "Doing something regularly", "Consistency leads to success."),
            Triple("Empower", "Give strength or confidence", "Education empowers people."),
            Triple("Grateful", "Feeling thankful", "I am grateful for today.")
        )

        btnNewWord.setOnClickListener {
            val randomWord = words.random()
            tvWord.text = randomWord.first
            tvMeaning.text = randomWord.second
            tvExample.text = randomWord.third
        }
    }
}
